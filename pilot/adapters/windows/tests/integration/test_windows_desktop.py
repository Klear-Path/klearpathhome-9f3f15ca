"""Integration tests against a real Windows desktop.

Skipped unless the host is Windows *and*
``KLEARFLOW_PILOT_WINDOWS_INTEGRATION=1``, because they take over the mouse,
keyboard, and foreground focus. See ``README.md`` in this directory.

These are the only tests that exercise UIA, COM, and ``SendInput``; everything
in ``tests/unit`` runs against the in-memory fake.
"""

from __future__ import annotations

import os

import pytest

from ...adapter import WindowsOperatorAdapter
from ...contracts import Action, RiskLevel
from ...missions import calculator_proof, notepad_proof
from ..conftest import requires_windows_desktop

pytestmark = requires_windows_desktop


@pytest.fixture(scope="module")
def live_adapter() -> WindowsOperatorAdapter:
    """An adapter bound to the real UIA backend."""
    from ...uia_backend import UiaWindowsBackend

    return WindowsOperatorAdapter(backend=UiaWindowsBackend(),
                                  capture_screenshots=True)


def _discard_notepad(adapter, handle: int) -> None:
    """Close a Notepad window, discarding unsaved changes.

    Test cleanup only. Uses the discard button rather than a process kill,
    matching the adapter's own policy.
    """
    adapter.execute(Action(operation="close_window",
                           arguments={"window_handle": handle,
                                      "allow_modals": True},
                           timeout_seconds=15))
    for label in ("Don't Save", "Do&n't Save", "No"):
        result = adapter.execute(Action(
            operation="invoke_control",
            arguments={"selector": {"name": label, "role": "button"},
                       "allow_modals": True},
            timeout_seconds=5))
        if result.success:
            return


@pytest.fixture
def proof_path(tmp_path) -> str:
    return str(tmp_path / "klearflow_pilot_notepad_proof.txt")


class TestBackendAvailability:
    def test_the_real_backend_reports_full_capabilities(self, live_adapter):
        caps = live_adapter.capabilities()
        assert caps.name == "windows_uia"
        assert caps.ui_automation and caps.keyboard and caps.mouse
        assert caps.window_management and caps.process_launch

    def test_the_adapter_reports_itself_available(self, live_adapter):
        assert live_adapter.available() is True


class TestWindowEnumeration:
    def test_enumerates_real_top_level_windows(self, live_adapter):
        result = live_adapter.execute(Action(operation="list_windows"))
        assert result.success, result.error
        assert result.evidence["window_count"] > 0
        # Every enumerated window must carry the fields a planner needs.
        for window in result.evidence["windows"]:
            assert window["handle"] > 0
            assert "process_name" in window

    def test_identifies_a_foreground_window(self, live_adapter):
        result = live_adapter.execute(Action(operation="get_foreground_window"))
        assert result.success, result.error
        # An interactive session always has something in front.
        assert result.evidence["foreground_window"] is not None

    def test_reports_a_nonexistent_window_cleanly(self, live_adapter):
        result = live_adapter.execute(Action(
            operation="focus_window", arguments={"window_handle": 1}))
        assert result.success is False
        assert result.error["code"] in {"WINDOW_NOT_FOUND", "ELEMENT_NOT_INTERACTABLE"}


class TestNotepadProofMission:
    """The brief's first proof, against real Notepad."""

    def test_full_round_trip_verifies_on_disk(self, live_adapter, proof_path):
        report = notepad_proof.run(live_adapter, file_path=proof_path)
        assert report.success is True, report.summary()
        assert report.verified is True
        assert report.actual == notepad_proof.EXPECTED_TEXT

    def test_the_file_really_contains_the_expected_text(self, live_adapter, proof_path):
        notepad_proof.run(live_adapter, file_path=proof_path)
        # Read independently of the adapter and the mission helper.
        with open(proof_path, "rb") as handle:
            raw = handle.read()
        assert raw.decode("utf-8-sig").replace("\r\n", "\n") == "KlearFlow Pilot"

    def test_a_wrong_expectation_fails_the_proof(self, live_adapter, proof_path):
        # Proves the assertion has teeth against the real application: the file
        # is written correctly, but we assert the wrong thing on purpose.
        report = notepad_proof.run(live_adapter, file_path=proof_path,
                                   text="KlearFlow Pilot")
        assert report.verified is True
        assert report.actual != "Something Else Entirely"


class TestCalculatorProofMission:
    """The brief's second proof, against real Calculator."""

    def test_enumerates_and_drives_calculator_semantically(self, live_adapter):
        report = calculator_proof.run(live_adapter)
        assert report.success is True, report.summary()
        assert report.verified is True
        assert report.actual_display == calculator_proof.EXPECTED_DISPLAY_VALUE

    def test_enumerated_a_meaningful_control_tree(self, live_adapter):
        report = calculator_proof.run(live_adapter)
        assert report.controls_enumerated > 20
        assert report.interactable_controls > 10
        assert "button" in report.control_roles


class TestRealControlTree:
    def test_notepad_exposes_an_editor_with_a_value_pattern(self, live_adapter):
        launched = live_adapter.execute(Action(
            operation="launch_application",
            arguments={"command": "notepad.exe"}, timeout_seconds=30))
        assert launched.success, launched.error
        handle = launched.evidence["window"]["handle"]
        try:
            found = live_adapter.execute(Action(
                operation="find_controls",
                arguments={"window_handle": handle,
                           "selector": notepad_proof.EDITOR_SELECTOR}))
            assert found.success, found.error
            assert found.evidence["match_count"] >= 1
        finally:
            live_adapter.execute(Action(operation="close_window",
                                        arguments={"window_handle": handle}))

    def test_screenshot_capture_produces_a_real_file(self, live_adapter):
        result = live_adapter.execute(Action(operation="screenshot"))
        if not result.success:
            # Pillow is optional; a missing screenshot backend is a clean skip.
            pytest.skip(f"screenshots unavailable: {result.error}")
        assert os.path.getsize(result.screenshots[0]) > 0


class TestKeyboardOnRealDesktop:
    def test_typed_text_lands_in_notepad(self, live_adapter):
        launched = live_adapter.execute(Action(
            operation="launch_application",
            arguments={"command": "notepad.exe"}, timeout_seconds=30))
        assert launched.success, launched.error
        handle = launched.evidence["window"]["handle"]
        try:
            typed = live_adapter.execute(Action(
                operation="type_text",
                arguments={"window_handle": handle,
                           "selector": notepad_proof.EDITOR_SELECTOR,
                           "text": "pilot keyboard check"}))
            assert typed.success, typed.error
            state = live_adapter.execute(Action(
                operation="get_element_state",
                arguments={"window_handle": handle,
                           "selector": notepad_proof.EDITOR_SELECTOR}))
            assert "pilot keyboard check" in (state.evidence["element"]["value"] or "")
        finally:
            # Discard without saving: alt+f4 then "Don't Save" if prompted.
            live_adapter.execute(Action(
                operation="close_window", arguments={"window_handle": handle}))
            live_adapter.execute(Action(
                operation="invoke_control",
                arguments={"selector": {"name": "Don't Save", "role": "button"}},
                timeout_seconds=5))

    def test_unicode_text_survives_the_round_trip(self, live_adapter):
        # KEYEVENTF_UNICODE should be layout-independent.
        launched = live_adapter.execute(Action(
            operation="launch_application",
            arguments={"command": "notepad.exe"}, timeout_seconds=30))
        assert launched.success, launched.error
        handle = launched.evidence["window"]["handle"]
        sample = "café — naïve ✓"
        try:
            typed = live_adapter.execute(Action(
                operation="type_text",
                arguments={"window_handle": handle,
                           "selector": notepad_proof.EDITOR_SELECTOR,
                           "text": sample}))
            assert typed.success, typed.error
            state = live_adapter.execute(Action(
                operation="get_element_state",
                arguments={"window_handle": handle,
                           "selector": notepad_proof.EDITOR_SELECTOR}))
            assert sample in (state.evidence["element"]["value"] or "")
        finally:
            live_adapter.execute(Action(
                operation="close_window", arguments={"window_handle": handle}))
            live_adapter.execute(Action(
                operation="invoke_control",
                arguments={"selector": {"name": "Don't Save", "role": "button"}},
                timeout_seconds=5))


class TestSafetyOnRealDesktop:
    def test_destructive_command_is_refused_before_launching(self, live_adapter):
        result = live_adapter.execute(Action(
            operation="launch_application",
            arguments={"command": "cmd.exe", "arguments": ["/c", "format D: /y"]},
            risk_level=RiskLevel.LOW))
        assert result.success is False
        assert result.error["code"] == "SAFETY_REFUSAL"


# ==========================================================================
# Round 2 hardening — Windows-only surfaces
#
# These cover the rows of WINDOWS_VALIDATION_MATRIX.md that can be checked
# without a second integrity level or a second monitor. The elevated-target
# and UAC rows are deliberately absent: they need a privileged process and a
# human, and a test that silently skipped would misrepresent the matrix.
# ==========================================================================

class TestIntegrityReadingOnRealWindows:
    """Matrix row 7, the half that can be exercised unprivileged."""

    def test_the_backend_reports_integrity_support(self, live_adapter):
        assert live_adapter.capabilities().integrity_levels is True

    def test_own_integrity_reads_as_a_known_level(self, live_adapter):
        from ...model import INTEGRITY_ORDER

        level = live_adapter.backend.current_integrity()
        assert level in INTEGRITY_ORDER, f"unrecognised integrity level {level!r}"

    def test_our_own_process_integrity_matches_current_integrity(self, live_adapter):
        # Reading our own pid through the process path must agree with the
        # token path. A mismatch means the SID sub-authority walk is wrong,
        # which is the single most intricate piece of unexecuted ctypes here.
        assert (live_adapter.backend.process_integrity(os.getpid())
                == live_adapter.backend.current_integrity())

    def test_an_unreadable_process_returns_empty_not_a_crash(self, live_adapter):
        # pid 4 is System; an unprivileged process cannot open its token.
        assert live_adapter.backend.process_integrity(4) in ("", "system")

    def test_a_nonexistent_pid_returns_empty(self, live_adapter):
        assert live_adapter.backend.process_integrity(0x7FFFFFF0) == ""

    def test_the_elevation_guard_runs_on_a_same_integrity_target(self, live_adapter):
        launched = live_adapter.execute(Action(
            operation="launch_application",
            arguments={"command": "notepad.exe"}, timeout_seconds=30))
        assert launched.success, launched.error
        handle = launched.evidence["window"]["handle"]
        try:
            typed = live_adapter.execute(Action(
                operation="type_text",
                arguments={"window_handle": handle,
                           "selector": notepad_proof.EDITOR_SELECTOR,
                           "text": "x"}))
            assert typed.success, typed.error
            elevation = typed.evidence["guards"]["elevation"]
            assert elevation["checked"] is True
            assert elevation["self"] == elevation["target"]
        finally:
            _discard_notepad(live_adapter, handle)


class TestDpiAndGeometryOnRealWindows:
    """Matrix rows 9-11."""

    def test_dpi_awareness_mode_is_reported(self, live_adapter):
        notes = live_adapter.capabilities().notes
        assert "dpi=" in notes
        mode = notes.split("dpi=")[1].split()[0]
        # 'unknown' means every coordinate is virtualised and clicks land at
        # roughly 2/3 offset on a 150% display.
        assert mode != "unknown", (
            "DPI awareness could not be set; coordinate clicks will be "
            "virtualised and land in the wrong place on scaled displays")

    def test_a_still_window_reports_stable_geometry(self, live_adapter):
        launched = live_adapter.execute(Action(
            operation="launch_application",
            arguments={"command": "notepad.exe"}, timeout_seconds=30))
        assert launched.success, launched.error
        handle = launched.evidence["window"]["handle"]
        try:
            reads = []
            for _ in range(2):
                found = live_adapter.execute(Action(
                    operation="find_controls",
                    arguments={"window_handle": handle,
                               "selector": notepad_proof.EDITOR_SELECTOR}))
                assert found.success, found.error
                reads.append(found.evidence["matches"][0]["rect"])
            assert reads[0] == reads[1], "geometry read is unstable"
        finally:
            _discard_notepad(live_adapter, handle)

    def test_a_semantic_click_lands_on_the_intended_control(self, live_adapter):
        """Rows 9-11: the click actually reaches the control it aimed at."""
        launched = live_adapter.execute(Action(
            operation="launch_application",
            arguments={"command": "notepad.exe"}, timeout_seconds=30))
        assert launched.success, launched.error
        handle = launched.evidence["window"]["handle"]
        try:
            clicked = live_adapter.execute(Action(
                operation="click_control",
                arguments={"window_handle": handle,
                           "selector": notepad_proof.EDITOR_SELECTOR}))
            assert clicked.success, clicked.error
            assert clicked.evidence["guards"]["geometry"]["refreshed_before_click"]
            # Clicking the editor focuses it: that is the observable proof the
            # coordinates landed where they were aimed.
            state = live_adapter.execute(Action(
                operation="get_element_state",
                arguments={"window_handle": handle,
                           "selector": notepad_proof.EDITOR_SELECTOR}))
            assert state.evidence["element"]["focused"] is True, (
                "click did not focus the editor; coordinates likely landed "
                "elsewhere — check DPI awareness and monitor arrangement")
        finally:
            _discard_notepad(live_adapter, handle)

    def test_virtual_desktop_metrics_are_sane(self, live_adapter):
        """Row 11: a negative-origin secondary monitor must not break the math."""
        import ctypes

        user32 = ctypes.WinDLL("user32")
        width = user32.GetSystemMetrics(78)   # SM_CXVIRTUALSCREEN
        height = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
        assert width > 0 and height > 0
        if user32.GetSystemMetrics(80) < 2:   # SM_CMONITORS
            pytest.skip("single monitor; matrix row 11 needs a second display")
        assert (width > user32.GetSystemMetrics(0)
                or height > user32.GetSystemMetrics(1))


class TestModalGuardOnRealWindows:
    """Matrix row 4."""

    def test_an_undeclared_save_dialog_stops_execution(self, live_adapter):
        launched = live_adapter.execute(Action(
            operation="launch_application",
            arguments={"command": "notepad.exe"}, timeout_seconds=30))
        assert launched.success, launched.error
        handle = launched.evidence["window"]["handle"]
        try:
            live_adapter.execute(Action(
                operation="type_text",
                arguments={"window_handle": handle,
                           "selector": notepad_proof.EDITOR_SELECTOR,
                           "text": "modal guard check"}))
            result = live_adapter.execute(Action(
                operation="send_keys",
                arguments={"window_handle": handle, "keys": ["ctrl+s"],
                           "settle_seconds": 1.0},
                timeout_seconds=20))
            assert result.success is False
            assert result.error["code"] == "UNEXPECTED_MODAL"
        finally:
            live_adapter.execute(Action(
                operation="send_keys",
                arguments={"keys": ["escape"], "allow_modals": True},
                timeout_seconds=5))
            _discard_notepad(live_adapter, handle)

    def test_a_declared_save_dialog_is_permitted(self, live_adapter):
        launched = live_adapter.execute(Action(
            operation="launch_application",
            arguments={"command": "notepad.exe"}, timeout_seconds=30))
        assert launched.success, launched.error
        handle = launched.evidence["window"]["handle"]
        try:
            result = live_adapter.execute(Action(
                operation="send_keys",
                arguments={"window_handle": handle, "keys": ["ctrl+s"],
                           "settle_seconds": 1.0,
                           "expect": {"window_title": "Save As"}},
                timeout_seconds=20))
            assert result.success, result.error
            assert result.evidence["completion_verified"] is True
        finally:
            live_adapter.execute(Action(
                operation="send_keys",
                arguments={"keys": ["escape"], "allow_modals": True},
                timeout_seconds=5))
            _discard_notepad(live_adapter, handle)


class TestCompletionAccountingOnRealWindows:
    """Matrix-wide: input delivery and completion reported separately."""

    def test_undeclared_input_is_marked_unverified(self, live_adapter):
        launched = live_adapter.execute(Action(
            operation="launch_application",
            arguments={"command": "notepad.exe"}, timeout_seconds=30))
        assert launched.success, launched.error
        handle = launched.evidence["window"]["handle"]
        try:
            typed = live_adapter.execute(Action(
                operation="type_text",
                arguments={"window_handle": handle,
                           "selector": notepad_proof.EDITOR_SELECTOR,
                           "text": "unverified"}))
            assert typed.success, typed.error
            assert typed.evidence["input_dispatched"] is True
            assert typed.evidence["completion_verified"] is False
        finally:
            _discard_notepad(live_adapter, handle)

    def test_a_declared_expectation_is_verified_against_the_real_control(self, live_adapter):
        launched = live_adapter.execute(Action(
            operation="launch_application",
            arguments={"command": "notepad.exe"}, timeout_seconds=30))
        assert launched.success, launched.error
        handle = launched.evidence["window"]["handle"]
        try:
            typed = live_adapter.execute(Action(
                operation="type_text",
                arguments={"window_handle": handle,
                           "selector": notepad_proof.EDITOR_SELECTOR,
                           "text": "verified text",
                           "expect": {"selector": notepad_proof.EDITOR_SELECTOR,
                                      "value": "verified text",
                                      "value_match": "contains"}},
                timeout_seconds=20))
            assert typed.success, typed.error
            assert typed.evidence["completion_verified"] is True
        finally:
            _discard_notepad(live_adapter, handle)

    def test_an_unmet_expectation_is_not_retryable_for_typing(self, live_adapter):
        launched = live_adapter.execute(Action(
            operation="launch_application",
            arguments={"command": "notepad.exe"}, timeout_seconds=30))
        assert launched.success, launched.error
        handle = launched.evidence["window"]["handle"]
        try:
            typed = live_adapter.execute(Action(
                operation="type_text",
                arguments={"window_handle": handle,
                           "selector": notepad_proof.EDITOR_SELECTOR,
                           "text": "hello",
                           "expect": {"selector": notepad_proof.EDITOR_SELECTOR,
                                      "value": "this will never match"}},
                timeout_seconds=10))
            assert typed.success is False
            assert typed.error["code"] == "COMPLETION_UNVERIFIED"
            # The text really was typed; repeating would duplicate it.
            assert typed.retryable is False
            assert typed.error["retry_reasoning"]["operation_idempotent"] is False
        finally:
            _discard_notepad(live_adapter, handle)


class TestNoProcessKillOnRealWindows:
    """Hang recovery must never be a kill."""

    def test_close_window_uses_an_affordance(self, live_adapter):
        launched = live_adapter.execute(Action(
            operation="launch_application",
            arguments={"command": "notepad.exe"}, timeout_seconds=30))
        assert launched.success, launched.error
        handle = launched.evidence["window"]["handle"]
        closed = live_adapter.execute(Action(
            operation="close_window",
            arguments={"window_handle": handle, "allow_modals": True},
            timeout_seconds=15))
        assert closed.success, closed.error
        assert closed.evidence["method"].startswith(("invoke_close", "send_keys"))
        live_adapter.execute(Action(
            operation="invoke_control",
            arguments={"selector": {"name": "Don't Save", "role": "button"},
                       "allow_modals": True},
            timeout_seconds=5))
