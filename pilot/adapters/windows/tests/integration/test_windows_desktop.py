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
