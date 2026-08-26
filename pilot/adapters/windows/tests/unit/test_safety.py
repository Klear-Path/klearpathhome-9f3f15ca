"""The confirmation gate.

The gate is additive: it can only withhold permission, never grant it. These
tests pin that it fails closed.
"""

from __future__ import annotations

import pytest

from ...adapter import WindowsOperatorAdapter
from ...contracts import Action, RiskLevel
from ...errors import SafetyRefusal
from ...safety import READ_ONLY_OPERATIONS, check, effective_risk


class TestEffectiveRisk:
    def test_read_only_operations_floor_at_read_only(self):
        # Even a mislabelled read is still a read.
        action = Action(operation="list_windows", risk_level=RiskLevel.HIGH)
        assert effective_risk(action) is RiskLevel.READ_ONLY

    def test_declared_risk_is_respected_for_mutating_operations(self):
        action = Action(operation="set_text", risk_level=RiskLevel.MEDIUM)
        assert effective_risk(action) is RiskLevel.MEDIUM

    @pytest.mark.parametrize("payload", [
        {"command": "cmd.exe", "arguments": ["/c", "format C: /y"]},
        {"command": "powershell", "arguments": ["Remove-Item -Recurse C:\\"]},
        {"text": "vssadmin delete shadows /all"},
        {"command": "shutdown /s /t 0"},
        {"command": "reg delete HKLM\\Software"},
    ])
    def test_destructive_payloads_are_escalated_to_high(self, payload):
        # A planner that labels `format c:` as low risk is exactly the case
        # worth catching, so the payload overrides the label.
        action = Action(operation="launch_application", arguments=payload,
                        risk_level=RiskLevel.LOW)
        assert effective_risk(action) is RiskLevel.HIGH

    def test_benign_payloads_are_not_escalated(self):
        action = Action(operation="launch_application",
                        arguments={"command": "notepad.exe"},
                        risk_level=RiskLevel.LOW)
        assert effective_risk(action) is RiskLevel.LOW

    def test_every_read_only_operation_is_registered(self):
        from ...operations import REGISTRY

        for name in READ_ONLY_OPERATIONS:
            assert name in REGISTRY, f"{name} is gated but not implemented"


class TestCheck:
    def test_allows_a_low_risk_action(self):
        decision = check(Action(operation="set_text", risk_level=RiskLevel.LOW))
        assert decision["allowed"] is True
        assert decision["effective_risk"] == "low"

    def test_refuses_high_risk_without_authorisation(self):
        with pytest.raises(SafetyRefusal) as info:
            check(Action(operation="set_text", risk_level=RiskLevel.HIGH))
        assert info.value.retryable is False

    def test_allows_high_risk_with_authorisation(self):
        decision = check(Action(operation="set_text", risk_level=RiskLevel.HIGH),
                         allow_high_risk=True)
        assert decision["allowed"] is True

    def test_refuses_a_destructive_payload_even_when_labelled_low(self):
        with pytest.raises(SafetyRefusal) as info:
            check(Action(operation="launch_application",
                         arguments={"command": "cmd /c format D: /y"},
                         risk_level=RiskLevel.LOW))
        assert info.value.details["matched_pattern"]

    def test_records_the_decision_for_evidence(self):
        decision = check(Action(operation="set_text", risk_level=RiskLevel.MEDIUM,
                                reversible=False))
        assert decision["declared_risk"] == "medium"
        assert decision["reversible"] is False
        assert decision["high_risk_allowed"] is False

    def test_read_only_operations_pass_regardless_of_label(self):
        assert check(Action(operation="list_windows",
                            risk_level=RiskLevel.HIGH))["allowed"] is True

    def test_unknown_risk_label_is_refused_by_default(self):
        # Action coercion floors an unknown label at HIGH; the gate then blocks.
        with pytest.raises(SafetyRefusal):
            check(Action(operation="set_text", risk_level="whatever"))


class TestGateInsideAdapter:
    def test_default_adapter_refuses_high_risk(self, adapter, notepad):
        result = adapter.execute(Action(operation="set_text",
                                        arguments={"text": "x"},
                                        risk_level=RiskLevel.HIGH))
        assert result.success is False
        assert result.error["code"] == "SAFETY_REFUSAL"

    def test_authorised_adapter_permits_high_risk(self, backend, notepad):
        adapter = WindowsOperatorAdapter(backend=backend, clock=backend.clock,
                                         allow_high_risk=True)
        result = adapter.execute(Action(
            operation="set_text",
            arguments={"window_handle": notepad.handle,
                       "selector": {"automation_id": "15"}, "text": "x"},
            risk_level=RiskLevel.HIGH))
        assert result.success is True

    def test_the_gate_runs_before_any_backend_call(self, adapter, backend, notepad):
        before = len(backend.calls)
        adapter.execute(Action(operation="launch_application",
                                arguments={"command": "cmd /c format C: /y"},
                                risk_level=RiskLevel.LOW))
        # No launch attempted: refusal must precede the side effect.
        assert ("launch", ("cmd /c format C: /y", ())) not in backend.calls[before:]

    def test_the_decision_appears_in_successful_evidence(self, adapter, notepad):
        result = adapter.execute(Action(operation="list_windows"))
        assert result.evidence["safety"]["effective_risk"] == "read_only"
