"""Proof mission 2: Calculator, driven without coordinates.

1. launch Calculator
2. enumerate its major UI controls (the control-tree inspection goal)
3. interact with semantic controls only — buttons resolved by automation id and
   accessible name, never by screen position
4. verify the resulting application state by reading the display control back

The arithmetic is chosen so the expected end state is unambiguous: 7 + 8 = 15.
A mission that merely "clicked something" would prove nothing, so the check is
on the display's value, and a wrong number fails.

Reading the display through the adapter is legitimate here, unlike the Notepad
file check: the display *is* the application's state, and there is no
out-of-band channel to observe it through. The independent-observer principle
applies to artefacts that outlive the app, not to in-app state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..adapter import WindowsOperatorAdapter
from ..contracts import Action, Result, RiskLevel

#: Buttons are addressed by automation id first, with the accessible name as a
#: fallback, because Calculator's names are localised but its automation ids
#: are not.
BUTTON_AUTOMATION_IDS = {
    "7": "num7Button",
    "8": "num8Button",
    "plus": "plusButton",
    "equals": "equalButton",
}

#: The result element's automation id is stable across Windows 10/11 builds.
DISPLAY_AUTOMATION_ID = "CalculatorResults"

EXPECTED_DISPLAY_VALUE = "15"


@dataclass
class CalculatorReport:
    name: str = "calculator_proof"
    success: bool = False
    verified: bool = False
    steps: list[dict[str, Any]] = field(default_factory=list)
    controls_enumerated: int = 0
    interactable_controls: int = 0
    control_roles: dict[str, int] = field(default_factory=dict)
    expected_display: str = EXPECTED_DISPLAY_VALUE
    actual_display: str | None = None
    inaccessible_controls: list[str] = field(default_factory=list)
    failure: str = ""
    results: list[Result] = field(default_factory=list, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "success": self.success,
            "verified": self.verified,
            "controls_enumerated": self.controls_enumerated,
            "interactable_controls": self.interactable_controls,
            "control_roles": self.control_roles,
            "expected_display": self.expected_display,
            "actual_display": self.actual_display,
            "inaccessible_controls": self.inaccessible_controls,
            "failure": self.failure,
            "steps": self.steps,
        }

    def summary(self) -> str:
        lines = [
            f"mission={self.name} success={self.success} verified={self.verified}",
            f"  enumerated {self.controls_enumerated} control(s), "
            f"{self.interactable_controls} interactable",
        ]
        for step in self.steps:
            status = "ok  " if step["success"] else "FAIL"
            lines.append(f"  [{status}] {step['operation']}: {step['detail']}")
        if self.failure:
            lines.append(f"  failure: {self.failure}")
        return "\n".join(lines)


def _record(report: CalculatorReport, operation: str, result: Result) -> bool:
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


def _digit_selector(key: str) -> dict[str, Any]:
    return {"automation_id": BUTTON_AUTOMATION_IDS[key], "role": "button"}


def run(adapter: WindowsOperatorAdapter, *,
        calculator_command: str = "calc.exe",
        mission_id: str = "proof-calculator") -> CalculatorReport:
    """Execute the Calculator proof mission."""
    report = CalculatorReport()

    def act(operation: str, arguments: dict[str, Any], *,
            timeout: float = 20.0) -> Result:
        return adapter.execute(Action(
            operation=operation, arguments=arguments, mission_id=mission_id,
            risk_level=RiskLevel.LOW, timeout_seconds=timeout,
            expected_result=f"{operation} succeeds",
        ))

    # 1. Launch. Calculator on Windows 10/11 is a packaged app started through
    #    a stub process, so the window may belong to a different pid — the
    #    adapter's launch path already handles that.
    launch = act("launch_application",
                 {"command": calculator_command,
                  "wait_for_window_seconds": 20.0},
                 timeout=45.0)
    if not _record(report, "launch_application", launch):
        return report
    window_handle = (launch.evidence.get("window") or {}).get("handle")

    # 2. Enumerate the control tree.
    tree = act("get_control_tree",
               {"window_handle": window_handle, "limit": 200, "max_depth": 14},
               timeout=30.0)
    if not _record(report, "get_control_tree", tree):
        return report
    stats = tree.evidence.get("stats") or {}
    report.controls_enumerated = int(stats.get("total_elements", 0))
    report.interactable_controls = int(stats.get("interactable_elements", 0))
    report.control_roles = dict(stats.get("roles") or {})
    # Goal 13: record any element advertising no accessible pattern, so the
    # integrator can see where a vision fallback would eventually be needed.
    report.inaccessible_controls = [
        f"{row.get('role')}:{row.get('name') or row.get('automation_id') or '<unnamed>'}"
        for row in (tree.evidence.get("elements") or [])
        if not row.get("patterns")
    ]

    if report.interactable_controls == 0:
        report.failure = ("Calculator exposed no interactable UIA controls; "
                          "cannot proceed without a vision fallback")
        report.steps.append({"operation": "verify_controls_present",
                             "success": False, "detail": report.failure,
                             "error_code": "UNSUPPORTED_UI", "retryable": False,
                             "duration_seconds": 0.0})
        return report

    # 3. Compute 7 + 8 = using semantic selectors only.
    for label in ("7", "plus", "8", "equals"):
        pressed = act("invoke_control",
                      {"window_handle": window_handle,
                       "selector": _digit_selector(label),
                       "settle_seconds": 0.25})
        if not _record(report, f"invoke_control({label})", pressed):
            return report

    # 4. Verify the resulting state via the display control.
    display = act("get_element_state",
                  {"window_handle": window_handle,
                   "selector": {"automation_id": DISPLAY_AUTOMATION_ID}})
    if not _record(report, "get_element_state(display)", display):
        return report

    element = display.evidence.get("element") or {}
    raw_value = element.get("value")
    raw_name = element.get("name") or ""
    # The real app reports the number in the value *or* in an accessible name
    # of the form "Display is 15"; accept either, but require the digits.
    candidate = (raw_value or "").strip()
    if not candidate and raw_name:
        candidate = raw_name.replace("Display is", "").strip()
    normalized = candidate.replace(",", "").replace(" ", "").strip()

    report.actual_display = normalized
    report.verified = normalized == EXPECTED_DISPLAY_VALUE
    report.steps.append({
        "operation": "verify_display",
        "success": report.verified,
        "detail": (f"display reads {normalized!r} as expected" if report.verified
                   else f"expected display {EXPECTED_DISPLAY_VALUE!r} but read "
                        f"{normalized!r} (value={raw_value!r} name={raw_name!r})"),
        "error_code": None if report.verified else "VERIFICATION_FAILED",
        "retryable": False,
        "duration_seconds": 0.0,
    })
    if not report.verified:
        report.failure = (f"calculator state mismatch: expected "
                          f"{EXPECTED_DISPLAY_VALUE!r}, read {normalized!r}")
        return report

    report.success = True
    return report


__all__ = [
    "run", "CalculatorReport", "EXPECTED_DISPLAY_VALUE",
    "BUTTON_AUTOMATION_IDS", "DISPLAY_AUTOMATION_ID",
]
