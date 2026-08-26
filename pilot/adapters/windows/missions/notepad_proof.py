"""Proof mission 1: Notepad round-trip.

Sequence, entirely through adapter Actions:

1. launch Notepad
2. locate the editor control by *semantics* (control type + Value pattern)
3. type "KlearFlow Pilot"
4. save to a known path via ctrl+s and the Save As dialog
5. close Notepad
6. read the file back from disk **outside the adapter**
7. assert the contents equal the expected text

Step 6 is deliberately a plain :func:`open`. Verifying a write by asking the
same component that performed it to read it back proves very little; the point
is an independent observer. The mission returns ``verified=False`` with the
actual bytes when they differ, so a wrong file can never read as success.

This is a scripted sequence, not a mission controller: no planning, no
branching, no retry policy. It exists to prove the adapter works.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from typing import Any

from ..adapter import WindowsOperatorAdapter
from ..contracts import Action, Result, RiskLevel

EXPECTED_TEXT = "KlearFlow Pilot"

#: Real Notepad writes CRLF. The assertion normalises line endings but nothing
#: else, so a mangled payload still fails.
_NEWLINE_VARIANTS = ("\r\n", "\r")


@dataclass
class MissionReport:
    """Outcome of a proof mission."""

    name: str
    success: bool
    verified: bool = False
    steps: list[dict[str, Any]] = field(default_factory=list)
    expected: str = ""
    actual: str | None = None
    file_path: str = ""
    failure: str = ""
    results: list[Result] = field(default_factory=list, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "success": self.success,
            "verified": self.verified,
            "expected": self.expected,
            "actual": self.actual,
            "file_path": self.file_path,
            "failure": self.failure,
            "steps": self.steps,
        }

    def summary(self) -> str:
        lines = [f"mission={self.name} success={self.success} verified={self.verified}"]
        for step in self.steps:
            status = "ok  " if step["success"] else "FAIL"
            lines.append(f"  [{status}] {step['operation']}: {step['detail']}")
        if self.failure:
            lines.append(f"  failure: {self.failure}")
        return "\n".join(lines)


def _record(report: MissionReport, operation: str, result: Result) -> bool:
    report.results.append(result)
    report.steps.append({
        "operation": operation,
        "success": result.success,
        "detail": result.stdout if result.success else (result.stderr or "failed"),
        "error_code": (result.error or {}).get("code"),
        "retryable": result.retryable,
        "duration_seconds": result.duration_seconds,
    })
    if not result.success:
        report.failure = (
            f"step '{operation}' failed: "
            f"{(result.error or {}).get('code', 'UNKNOWN')} - "
            f"{(result.error or {}).get('message', result.stderr)}"
        )
    return result.success


def _note(report: MissionReport, operation: str, detail: str, *,
          code: str = "VERIFICATION_FAILED") -> None:
    report.failure = detail
    report.steps.append({
        "operation": operation, "success": False, "detail": detail,
        "error_code": code, "retryable": False, "duration_seconds": 0.0,
    })


def default_output_path() -> str:
    """A predictable, writable target path for the proof."""
    directory = os.environ.get("KLEARFLOW_PILOT_TEST_DIR") or tempfile.gettempdir()
    return os.path.join(directory, "klearflow_pilot_notepad_proof.txt")


def read_back(path: str) -> str:
    """Read the saved file independently of the adapter.

    Byte-level read then explicit decode, so a wrong encoding is noticed rather
    than papered over by implicit text-mode decoding.
    """
    with open(path, "rb") as handle:
        raw = handle.read()
    text = raw.decode("utf-8-sig")
    for variant in _NEWLINE_VARIANTS:
        text = text.replace(variant, "\n")
    return text


#: Notepad's editor is a Document-role control exposing a Value pattern. Asking
#: for the *pattern* rather than a class name is what keeps this working across
#: Windows builds, where the editor class changed from ``Edit`` to
#: ``RichEditD2DPT``.
EDITOR_SELECTOR: dict[str, Any] = {
    "role": "document",
    "requires_patterns": ["value"],
    "focusable_only": True,
}

SAVE_AS_FILENAME_SELECTOR: dict[str, Any] = {
    "role": "edit",
    "requires_patterns": ["value"],
    "focusable_only": True,
}


def run(adapter: WindowsOperatorAdapter, *,
        text: str = EXPECTED_TEXT,
        file_path: str | None = None,
        notepad_command: str = "notepad.exe",
        close_when_done: bool = True,
        mission_id: str = "proof-notepad") -> MissionReport:
    """Execute the Notepad proof mission."""
    target = file_path or default_output_path()
    report = MissionReport(name="notepad_proof", success=False,
                           expected=text, file_path=target)

    # Start clean so a stale file from an earlier run cannot make a failed save
    # look like a success.
    if os.path.exists(target):
        os.remove(target)

    def act(operation: str, arguments: dict[str, Any], *,
            risk: RiskLevel = RiskLevel.LOW, timeout: float = 20.0,
            reversible: bool = True) -> Result:
        return adapter.execute(Action(
            operation=operation, arguments=arguments, mission_id=mission_id,
            risk_level=risk, timeout_seconds=timeout, reversible=reversible,
            expected_result=f"{operation} succeeds",
        ))

    # 1. Launch.
    launch = act("launch_application",
                 {"command": notepad_command, "wait_for_window_seconds": 10.0},
                 timeout=30.0)
    if not _record(report, "launch_application", launch):
        return report
    window_handle = (launch.evidence.get("window") or {}).get("handle")

    # 2. Identify the editor control semantically.
    found = act("find_controls",
                {"window_handle": window_handle, "selector": EDITOR_SELECTOR})
    if not _record(report, "find_controls(editor)", found):
        return report
    if found.evidence.get("match_count", 0) < 1:
        _note(report, "find_controls(editor)",
              "no Document control exposing a Value pattern found in Notepad",
              code="ELEMENT_NOT_FOUND")
        return report

    # 3. Enter the text. set_text goes through ValuePattern and self-verifies,
    #    which is both faster and more reliable than synthesising keystrokes.
    typed = act("set_text",
                {"window_handle": window_handle, "selector": EDITOR_SELECTOR,
                 "text": text, "verify": True})
    if not _record(report, "set_text", typed):
        return report

    # 4. Save: ctrl+s, then drive the Save As dialog by name / automation id.
    save = act("send_keys",
               {"window_handle": window_handle, "keys": ["ctrl+s"],
                "settle_seconds": 0.6})
    if not _record(report, "send_keys(ctrl+s)", save):
        return report

    filename_field = act("set_text",
                         {"window_title": "Save As",
                          "selector": SAVE_AS_FILENAME_SELECTOR,
                          "text": target, "verify": True})
    if not _record(report, "set_text(save_as_filename)", filename_field):
        return report

    # Writing the file is the one genuinely irreversible step, so it is
    # labelled as such rather than hidden behind the permissive default.
    confirm = act("invoke_control",
                  {"window_title": "Save As",
                   "selector": {"name": "Save", "role": "button",
                                "name_match": "iequals"},
                   "settle_seconds": 0.8},
                  risk=RiskLevel.MEDIUM, reversible=False)
    if not _record(report, "invoke_control(Save)", confirm):
        return report

    # 5. Close Notepad via its Close affordance / alt+f4 — never a process kill.
    #    Non-fatal: the file is already on disk, and verification is what
    #    decides the mission.
    if close_when_done:
        closed = act("close_window",
                     {"window_handle": window_handle, "settle_seconds": 0.5})
        _record(report, "close_window", closed)
        if not closed.success:
            report.failure = ""  # do not let a stuck window mask verification

    # 6 & 7. Independent verification.
    if not os.path.exists(target):
        _note(report, "verify_file_exists",
              f"expected file was not created: {target}")
        return report

    actual = read_back(target)
    report.actual = actual
    report.verified = actual == text
    report.steps.append({
        "operation": "verify_file_contents",
        "success": report.verified,
        "detail": (f"file contents match expected {text!r}" if report.verified
                   else f"expected {text!r} but file contained {actual!r}"),
        "error_code": None if report.verified else "VERIFICATION_FAILED",
        "retryable": False,
        "duration_seconds": 0.0,
    })
    if not report.verified:
        report.failure = (f"file contents mismatch: expected {text!r}, "
                          f"got {actual!r}")
        return report

    report.success = True
    return report


__all__ = [
    "run", "MissionReport", "EXPECTED_TEXT",
    "default_output_path", "read_back",
    "EDITOR_SELECTOR", "SAVE_AS_FILENAME_SELECTOR",
]
