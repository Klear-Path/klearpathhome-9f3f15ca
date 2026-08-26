"""Evidence capture policy."""

from __future__ import annotations

import os

from ...evidence import CapturePolicy, capture_screenshot, capture_state


class TestCapturePolicy:
    def test_minimal_captures_only_the_foreground(self):
        policy = CapturePolicy.minimal()
        assert policy.foreground and not policy.window_list
        assert not policy.control_tree and not policy.screenshot

    def test_full_captures_everything(self):
        policy = CapturePolicy.full()
        assert all([policy.foreground, policy.window_list,
                    policy.control_tree, policy.screenshot])


class TestCaptureState:
    def test_captures_the_requested_fields(self, backend, notepad):
        state = capture_state(backend, CapturePolicy.standard(), label="before")
        assert state["label"] == "before"
        assert state["foreground_window"]["title"] == "Untitled - Notepad"
        assert len(state["windows"]) == 1
        assert state["capture_errors"] == []

    def test_skips_fields_the_policy_excludes(self, backend, notepad):
        state = capture_state(backend, CapturePolicy.minimal(), label="x")
        assert "windows" not in state

    def test_captures_a_control_tree_when_asked(self, backend, notepad):
        state = capture_state(backend, CapturePolicy(control_tree=True),
                              label="x", window_handle=notepad.handle)
        assert state["control_tree"]["stats"]["total_elements"] > 1

    def test_a_capture_error_is_recorded_not_raised(self, backend, notepad):
        # Evidence must never break an action.
        def boom(*_args, **_kwargs):
            raise RuntimeError("UIA unavailable")

        backend.list_windows = boom
        state = capture_state(backend, CapturePolicy.standard(), label="x")
        assert state["capture_errors"][0]["field"] == "windows"
        assert "UIA unavailable" in state["capture_errors"][0]["error"]

    def test_partial_failure_keeps_the_successful_fields(self, backend, notepad):
        def boom(*_args, **_kwargs):
            raise RuntimeError("nope")

        backend.list_windows = boom
        state = capture_state(backend, CapturePolicy.standard(), label="x")
        assert state["foreground_window"] is not None
        assert state["capture_errors"]


class TestCaptureScreenshot:
    def test_writes_a_file(self, backend, notepad, tmp_path, monkeypatch):
        monkeypatch.setenv("KLEARFLOW_PILOT_EVIDENCE_DIR", str(tmp_path))
        path, error = capture_screenshot(backend, label="shot")
        assert error is None
        assert path and os.path.exists(path)

    def test_honours_the_evidence_dir_override(self, backend, notepad, tmp_path, monkeypatch):
        monkeypatch.setenv("KLEARFLOW_PILOT_EVIDENCE_DIR", str(tmp_path))
        path, _ = capture_screenshot(backend, label="shot")
        assert str(tmp_path) in path

    def test_reports_an_unsupported_backend_without_raising(self, backend, notepad):
        backend.supports_screenshots = False
        path, error = capture_screenshot(backend, label="shot")
        assert path is None
        assert "no screenshot support" in error["error"]

    def test_reports_a_throwing_backend_without_raising(self, backend, notepad, tmp_path, monkeypatch):
        monkeypatch.setenv("KLEARFLOW_PILOT_EVIDENCE_DIR", str(tmp_path))

        def boom(*_args, **_kwargs):
            raise RuntimeError("GDI failure")

        backend.screenshot = boom
        path, error = capture_screenshot(backend, label="shot")
        assert path is None
        assert "GDI failure" in error["error"]
