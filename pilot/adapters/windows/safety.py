"""Confirmation gate for risky actions.

This does not replace or weaken any existing KlearForge safety system — it is
an additional, adapter-local check so that a desktop-controlling tool cannot
be talked into an irreversible action without the planner having said so
explicitly. If the core runtime already gates risk, this layer is redundant
and harmless; it never *grants* permission, it only withholds it.
"""

from __future__ import annotations

from typing import Any

from .contracts import Action, RiskLevel
from .errors import SafetyRefusal

#: Operations that only observe. Always allowed.
READ_ONLY_OPERATIONS = frozenset({
    "list_windows",
    "get_foreground_window",
    "get_control_tree",
    "find_controls",
    "get_element_state",
    "capabilities",
    "screenshot",
})

#: Substrings that, appearing in a launch command or typed text, suggest the
#: action could destroy data. Matching one does not block the action; it raises
#: the effective risk so the confirmation gate applies. Deliberately
#: conservative and easy to extend.
DESTRUCTIVE_HINTS = (
    "format ", "del /", "rmdir /s", "rd /s", "diskpart", "vssadmin delete",
    "cipher /w", "reg delete", "shutdown", "bcdedit", "takeown /f",
    "remove-item -recurse", "clear-disk", "remove-partition",
)


def _mentions_destructive_pattern(action: Action) -> str | None:
    haystacks: list[str] = []
    for key in ("command", "arguments", "text", "value", "path"):
        raw = action.arg(key)
        if isinstance(raw, str):
            haystacks.append(raw)
        elif isinstance(raw, (list, tuple)):
            haystacks.extend(str(x) for x in raw)
    blob = " ".join(haystacks).lower()
    for hint in DESTRUCTIVE_HINTS:
        if hint in blob:
            return hint
    return None


def effective_risk(action: Action) -> RiskLevel:
    """The risk level the gate actually enforces.

    Read-only operations floor at ``READ_ONLY``. Anything whose payload looks
    destructive is raised to ``HIGH`` regardless of what the planner claimed,
    because a planner that mislabels ``format c:`` as low risk is exactly the
    case worth catching.
    """
    if action.operation in READ_ONLY_OPERATIONS:
        return RiskLevel.READ_ONLY
    if _mentions_destructive_pattern(action):
        return RiskLevel.HIGH
    return action.risk_level


def check(action: Action, *, allow_high_risk: bool = False) -> dict[str, Any]:
    """Authorise ``action`` or raise :class:`SafetyRefusal`.

    Returns a decision record that is attached to the Result's evidence, so
    every executed action carries a note of what the gate concluded.

    ``allow_high_risk`` is the adapter-construction-time switch the core
    runtime flips once it has obtained operator consent. It defaults to off:
    an adapter built with no arguments cannot perform a high-risk irreversible
    action, which is the safe direction to fail.
    """
    risk = effective_risk(action)
    hint = _mentions_destructive_pattern(action)
    decision = {
        "declared_risk": action.risk_level.value,
        "effective_risk": risk.value,
        "reversible": action.reversible,
        "destructive_pattern": hint,
        "high_risk_allowed": allow_high_risk,
    }

    if hint and not allow_high_risk:
        raise SafetyRefusal(
            f"action payload matches destructive pattern {hint!r}; "
            "refusing without explicit high-risk authorisation",
            details={**decision, "matched_pattern": hint},
        )

    if risk is RiskLevel.HIGH and not allow_high_risk:
        raise SafetyRefusal(
            "action is high risk and this adapter was not authorised for "
            "high-risk operations",
            details=decision,
        )

    if risk is RiskLevel.HIGH and not action.reversible and not allow_high_risk:
        raise SafetyRefusal(
            "action is high risk and irreversible",
            details=decision,
        )

    decision["allowed"] = True
    return decision


__all__ = ["check", "effective_risk", "READ_ONLY_OPERATIONS", "DESTRUCTIVE_HINTS"]
