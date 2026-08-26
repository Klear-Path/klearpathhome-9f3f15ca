"""The execute envelope: Result shape, evidence, timeouts, and crash safety."""

from __future__ import annotations

from ...adapter import WindowsOperatorAdapter, default_backend
from ...backend import NullBackend
from ...contracts import Action


class TestDescribe:
    def test_reports_platform_and_operations(self, adapter):
        described = adapter.describe()
        assert described["tool"] == "windows_operator"
        assert described["available"] is True
        assert "set_text" in described["operations"]
        assert described["allow_high_risk"] is False

    def test_null_backend_reports_unavailable_with_a_reason(self):
        adapter = WindowsOperatorAdapter(backend=NullBackend("no desktop here"))
        assert adapter.available() is False
        assert "no desktop here" in adapter.capabilities().notes

    def test_default_backend_never_raises_on_this_host(self):
        # Constructibility on any platform is a hard requirement: the core
        # runtime must be able to introspect the adapter before deciding to use
        # it, including on a Linux build machine.
        backend = default_backend()
        assert backend.capabilities() is not None


class TestResultEnvelope:
    def test_success_populates_the_full_contract(self, adapter, notepad):
        result = adapter.execute(Action(operation="list_windows", id="act-1"))
        assert result.action_id == "act-1"
        assert result.success is True
        assert result.error is None
        assert result.retryable is False
        assert result.duration_seconds >= 0.0
        assert result.stdout
        assert result.evidence["operation"] == "list_windows"
        assert result.evidence["tool"] == "windows_operator"

    def test_evidence_records_the_backend_used(self, adapter, notepad):
        result = adapter.execute(Action(operation="list_windows"))
        assert result.evidence["backend"]["name"] == "fake"

    def test_state_is_captured_before_and_after(self, adapter, notepad):
        result = adapter.execute(Action(
            operation="focus_window",
            arguments={"window_handle": notepad.handle}))
        assert result.state_before["label"] == "before"
        assert result.state_after["label"] == "after"
        assert "windows" in result.state_after

    def test_failure_populates_error_and_stderr(self, adapter, notepad):
        result = adapter.execute(Action(operation="focus_window",
                                        arguments={"window_handle": 424242}))
        assert result.success is False
        assert result.error["code"] == "WINDOW_NOT_FOUND"
        assert result.stderr == result.error["message"]
        assert result.retryable is True

    def test_failure_still_captures_post_failure_state(self, adapter, notepad):
        # Which dialog actually appeared is often the most valuable evidence.
        result = adapter.execute(Action(operation="focus_window",
                                        arguments={"window_handle": 424242}))
        assert result.state_after["label"] == "after_failure"

    def test_failure_echoes_the_arguments_for_diagnosis(self, adapter, notepad):
        result = adapter.execute(Action(operation="focus_window",
                                        arguments={"window_handle": 424242}))
        assert result.evidence["arguments"] == {"window_handle": 424242}

    def test_result_is_json_serialisable(self, adapter, notepad):
        import json

        payload = adapter.execute(Action(operation="list_windows")).to_dict()
        assert json.loads(json.dumps(payload))["success"] is True


class TestNeverRaises:
    def test_a_malformed_action_becomes_a_result(self, adapter):
        result = adapter.execute({"arguments": {}})  # no operation
        assert result.success is False
        assert result.error["code"] == "INTERNAL_ERROR"

    def test_a_malformed_action_keeps_a_supplied_id(self, adapter):
        result = adapter.execute({"id": "bad-1"})
        assert result.action_id == "bad-1"

    def test_a_backend_that_explodes_becomes_a_result(self, adapter, backend, notepad):
        def boom(*_args, **_kwargs):
            raise RuntimeError("COM went sideways")

        backend.list_windows = boom
        result = adapter.execute(Action(operation="list_windows"))
        assert result.success is False
        assert result.error["code"] == "INTERNAL_ERROR"
        assert "COM went sideways" in result.error["message"]
        assert result.retryable is False

    def test_a_backend_raising_a_classified_error_keeps_its_code(self, adapter, backend, notepad):
        from ...errors import BackendError

        def boom(*_args, **_kwargs):
            raise BackendError("transient COM failure")

        backend.list_windows = boom
        result = adapter.execute(Action(operation="list_windows"))
        assert result.error["code"] == "BACKEND_ERROR"
        assert result.retryable is True

    def test_evidence_capture_failure_does_not_fail_the_action(self, adapter, backend, notepad):
        # Evidence is best-effort; an action that worked must still report so.
        def boom(*_args, **_kwargs):
            raise RuntimeError("cannot read foreground")

        backend.foreground_window = boom
        result = adapter.execute(Action(
            operation="invoke_control",
            arguments={"window_handle": notepad.handle,
                       "selector": {"name": "File", "role": "menu_item"}}))
        assert result.success is True
        assert result.state_before["capture_errors"]


class TestPlatformGating:
    def test_null_backend_fails_actions_with_platform_unavailable(self):
        adapter = WindowsOperatorAdapter(backend=NullBackend("not windows"))
        result = adapter.execute(Action(operation="list_windows"))
        assert result.success is False
        assert result.error["code"] == "PLATFORM_UNAVAILABLE"
        assert result.retryable is False
        assert "not windows" in result.error["message"]

    def test_a_capable_backend_missing_one_facility_is_unsupported_operation(self, backend, notepad):
        # Distinguishing "no desktop at all" from "no screenshots" matters: the
        # planner's response differs completely.
        backend.supports_screenshots = False
        adapter = WindowsOperatorAdapter(backend=backend, clock=backend.clock)
        result = adapter.execute(Action(operation="screenshot"))
        assert result.error["code"] == "UNSUPPORTED_OPERATION"
        assert result.error["details"]["missing"] == ["screenshots"]


class TestTimeouts:
    def test_a_missing_element_times_out_with_diagnostics(self, backend, notepad):
        adapter = WindowsOperatorAdapter(backend=backend, clock=backend.clock)
        result = adapter.execute(Action(
            operation="wait_for_element",
            arguments={"window_handle": notepad.handle,
                       "selector": {"name": "Never appears"},
                       "poll_interval_seconds": 0.25},
            timeout_seconds=1.0))
        assert result.success is False
        # The selector diagnosis is more actionable than a bare timeout.
        assert result.error["code"] == "ELEMENT_NOT_FOUND"
        assert backend.slept >= 1.0

    def test_an_element_appearing_late_is_found(self, backend, notepad):
        adapter = WindowsOperatorAdapter(backend=backend, clock=backend.clock)
        from ...fakes import FakeElement
        from ...model import PATTERN_INVOKE

        original_sleep = backend.sleep
        state = {"ticks": 0}

        def delayed_sleep(seconds):
            state["ticks"] += 1
            if state["ticks"] == 2:
                notepad.root.children.append(FakeElement(
                    runtime_id="late", name="Ready", role="button",
                    patterns=(PATTERN_INVOKE,), keyboard_focusable=True))
            original_sleep(seconds)

        backend.sleep = delayed_sleep
        result = adapter.execute(Action(
            operation="wait_for_element",
            arguments={"window_handle": notepad.handle,
                       "selector": {"name": "Ready"}},
            timeout_seconds=5.0))
        assert result.success is True
        assert result.evidence["waited_seconds"] > 0

    def test_duration_is_measured_from_the_injected_clock(self, backend, notepad):
        adapter = WindowsOperatorAdapter(backend=backend, clock=backend.clock)
        result = adapter.execute(Action(
            operation="invoke_control",
            arguments={"window_handle": notepad.handle,
                       "selector": {"name": "File", "role": "menu_item"},
                       "settle_seconds": 0.5}))
        assert result.duration_seconds >= 0.5


class TestExecuteAll:
    def test_runs_actions_in_order(self, adapter, calculator):
        results = adapter.execute_all([
            Action(operation="invoke_control",
                   arguments={"window_handle": calculator.handle,
                              "selector": {"automation_id": "num7Button"}}),
            Action(operation="get_element_state",
                   arguments={"window_handle": calculator.handle,
                              "selector": {"automation_id": "CalculatorResults"}}),
        ])
        assert all(r.success for r in results)
        assert results[1].evidence["element"]["value"] == "7"

    def test_stops_on_the_first_failure_by_default(self, adapter, calculator):
        # Pushing keystrokes into an app that failed to launch is worse than
        # stopping.
        results = adapter.execute_all([
            Action(operation="focus_window", arguments={"window_handle": 999999}),
            Action(operation="list_windows"),
        ])
        assert len(results) == 1
        assert results[0].success is False

    def test_can_be_told_to_continue(self, adapter, calculator):
        results = adapter.execute_all([
            Action(operation="focus_window", arguments={"window_handle": 999999}),
            Action(operation="list_windows"),
        ], stop_on_failure=False)
        assert len(results) == 2
        assert results[1].success is True
