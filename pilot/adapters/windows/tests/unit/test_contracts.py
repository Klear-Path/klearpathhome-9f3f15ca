"""Action/Result contract behaviour."""

from __future__ import annotations

import pytest

from ...contracts import (
    DEFAULT_TIMEOUT_SECONDS,
    Action,
    Result,
    RiskLevel,
    TOOL_NAME,
    coerce_action,
)
from ...errors import InvalidArguments


class TestAction:
    def test_generates_an_id_when_absent(self):
        action = Action(operation="list_windows")
        assert action.id.startswith("act_")

    def test_preserves_a_supplied_id(self):
        assert Action(operation="list_windows", id="abc").id == "abc"

    def test_defaults_tool_to_this_adapter(self):
        assert Action(operation="list_windows").tool == TOOL_NAME

    def test_rejects_an_empty_operation(self):
        with pytest.raises(ValueError):
            Action(operation="")

    @pytest.mark.parametrize("raw,expected", [
        ("high", RiskLevel.HIGH),
        ("LOW", RiskLevel.LOW),
        ("read_only", RiskLevel.READ_ONLY),
        (RiskLevel.MEDIUM, RiskLevel.MEDIUM),
    ])
    def test_coerces_risk_level_strings(self, raw, expected):
        assert Action(operation="x", risk_level=raw).risk_level is expected

    def test_unknown_risk_level_fails_closed_to_high(self):
        # A mislabelled risk must never become permissive.
        assert Action(operation="x", risk_level="banana").risk_level is RiskLevel.HIGH

    def test_none_risk_level_defaults_to_low(self):
        assert Action(operation="x", risk_level=None).risk_level is RiskLevel.LOW

    @pytest.mark.parametrize("bad", [0, -5, "nonsense", None])
    def test_invalid_timeout_falls_back_to_default(self, bad):
        assert Action(operation="x", timeout_seconds=bad).timeout_seconds == DEFAULT_TIMEOUT_SECONDS

    def test_require_returns_present_argument(self):
        assert Action(operation="x", arguments={"a": 1}).require("a") == 1

    def test_require_raises_structured_error_when_missing(self):
        with pytest.raises(InvalidArguments) as info:
            Action(operation="set_text").require("text")
        assert info.value.details["missing_argument"] == "text"
        assert info.value.retryable is False

    def test_require_treats_none_as_missing(self):
        with pytest.raises(InvalidArguments):
            Action(operation="set_text", arguments={"text": None}).require("text")

    def test_to_dict_is_json_friendly(self):
        payload = Action(operation="x", risk_level="high").to_dict()
        assert payload["risk_level"] == "high"
        assert set(payload) >= {
            "id", "mission_id", "tool", "operation", "arguments",
            "expected_result", "risk_level", "timeout_seconds", "reversible",
        }


class TestCoerceAction:
    def test_passes_through_an_action(self):
        action = Action(operation="x")
        assert coerce_action(action) is action

    def test_accepts_a_mapping(self):
        action = coerce_action({
            "operation": "set_text", "arguments": {"text": "hi"},
            "risk_level": "medium", "mission_id": "m1", "reversible": False,
        })
        assert action.operation == "set_text"
        assert action.risk_level is RiskLevel.MEDIUM
        assert action.mission_id == "m1"
        assert action.reversible is False

    def test_accepts_a_foreign_object_with_matching_attributes(self):
        # This is the seam that lets the core runtime pass its own Action type.
        class ForeignAction:
            operation = "list_windows"
            arguments = {"visible_only": False}
            id = "foreign-1"
            mission_id = "m9"
            tool = "windows_operator"
            expected_result = "windows listed"
            risk_level = "read_only"
            timeout_seconds = 5
            reversible = True

        action = coerce_action(ForeignAction())
        assert action.id == "foreign-1"
        assert action.arguments == {"visible_only": False}
        assert action.timeout_seconds == 5

    def test_missing_operation_is_rejected(self):
        with pytest.raises(ValueError):
            coerce_action({"arguments": {}})


class TestResult:
    def test_defaults_are_empty_not_none(self):
        result = Result(action_id="a", success=True)
        assert result.state_before == {} and result.screenshots == []
        assert result.error is None and result.retryable is False

    def test_to_dict_round_trips_all_contract_fields(self):
        payload = Result(action_id="a", success=True).to_dict()
        assert set(payload) == {
            "action_id", "success", "state_before", "state_after", "evidence",
            "stdout", "stderr", "screenshots", "error", "retryable",
            "duration_seconds",
        }
