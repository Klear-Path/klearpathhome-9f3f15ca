"""Pilot Action -> Result contract, as consumed by the Windows operator adapter.

This module is a *mirror* of the common Pilot contract, not a competing
definition of it. The adapter is designed to be handed the core runtime's own
Action/Result types instead: everything in this lane goes through
:func:`coerce_action` on the way in and :meth:`Result.to_dict` on the way out,
so the integrator can swap these dataclasses for the canonical ones by
adjusting only this file. See README.md ("Swapping in the canonical
contract").

No mission planning, scheduling, or retry policy lives here. The adapter
executes exactly one Action per call and reports what happened; deciding what
to do next is the mission controller's job.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Mapping


class RiskLevel(str, Enum):
    """How much damage a mis-executed action could do.

    The adapter does not *decide* risk; the planner sets it. The adapter reads
    it to know whether a confirmation gate applies (see
    :mod:`pilot.adapters.windows.safety`).
    """

    READ_ONLY = "read_only"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @classmethod
    def coerce(cls, value: Any) -> "RiskLevel":
        if isinstance(value, cls):
            return value
        if value is None:
            return cls.LOW
        try:
            return cls(str(value).strip().lower())
        except ValueError:
            # An unrecognised risk label must never silently downgrade to
            # permissive. Fail closed at the strictest level.
            return cls.HIGH


DEFAULT_TIMEOUT_SECONDS = 20.0

#: Identifier the core runtime uses to route an Action to this adapter.
TOOL_NAME = "windows_operator"


@dataclass(frozen=True)
class Action:
    """A single unit of computer work requested of this adapter."""

    operation: str
    arguments: Mapping[str, Any] = field(default_factory=dict)
    id: str = ""
    mission_id: str = ""
    tool: str = TOOL_NAME
    expected_result: str = ""
    risk_level: RiskLevel = RiskLevel.LOW
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    reversible: bool = True

    def __post_init__(self) -> None:
        if not self.operation or not str(self.operation).strip():
            raise ValueError("Action.operation is required")
        if not self.id:
            object.__setattr__(self, "id", f"act_{uuid.uuid4().hex[:12]}")
        if self.arguments is None:
            object.__setattr__(self, "arguments", {})
        object.__setattr__(self, "risk_level", RiskLevel.coerce(self.risk_level))
        try:
            timeout = float(self.timeout_seconds)
        except (TypeError, ValueError):
            timeout = DEFAULT_TIMEOUT_SECONDS
        if timeout <= 0:
            timeout = DEFAULT_TIMEOUT_SECONDS
        object.__setattr__(self, "timeout_seconds", timeout)

    def arg(self, name: str, default: Any = None) -> Any:
        return self.arguments.get(name, default)

    def require(self, name: str) -> Any:
        """Fetch a mandatory argument.

        Raises :class:`~pilot.adapters.windows.errors.InvalidArguments` so the
        adapter reports a structured failure rather than a bare ``KeyError``.
        """
        from .errors import InvalidArguments

        if name not in self.arguments or self.arguments[name] is None:
            raise InvalidArguments(
                f"operation '{self.operation}' requires argument '{name}'",
                details={"missing_argument": name, "operation": self.operation},
            )
        return self.arguments[name]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["risk_level"] = self.risk_level.value
        payload["arguments"] = dict(self.arguments)
        return payload


def coerce_action(candidate: Any) -> Action:
    """Accept an :class:`Action`, a mapping, or any object with the same fields.

    This is the single seam through which foreign Action representations enter
    the lane, so the core runtime can pass its own type without this adapter
    importing it.
    """
    if isinstance(candidate, Action):
        return candidate
    if isinstance(candidate, Mapping):
        source: Mapping[str, Any] = candidate
        get = source.get
    else:
        get = lambda key, default=None: getattr(candidate, key, default)  # noqa: E731
    kwargs: dict[str, Any] = {
        "operation": get("operation", "") or "",
        "arguments": get("arguments", None) or {},
        "id": get("id", "") or "",
        "mission_id": get("mission_id", "") or "",
        "tool": get("tool", TOOL_NAME) or TOOL_NAME,
        "expected_result": get("expected_result", "") or "",
        "risk_level": get("risk_level", RiskLevel.LOW),
        "reversible": bool(get("reversible", True)),
    }
    timeout = get("timeout_seconds", None)
    if timeout is not None:
        kwargs["timeout_seconds"] = timeout
    return Action(**kwargs)


@dataclass
class Result:
    """The outcome of one Action.

    ``success=False`` is a normal, expected value. The adapter converts every
    failure it can name into a Result; it raises only on programmer error.
    """

    action_id: str
    success: bool
    state_before: dict[str, Any] = field(default_factory=dict)
    state_after: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)
    stdout: str = ""
    stderr: str = ""
    screenshots: list[str] = field(default_factory=list)
    error: dict[str, Any] | None = None
    retryable: bool = False
    duration_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class _Clock:
    """Indirection over ``time.monotonic`` so duration is testable."""

    def __call__(self) -> float:
        return time.monotonic()


DEFAULT_CLOCK = _Clock()


def new_result(action: Action, **overrides: Any) -> Result:
    """Build a Result already bound to ``action``'s id."""
    return Result(action_id=action.id, success=bool(overrides.pop("success", False)), **overrides)


__all__ = [
    "Action",
    "Result",
    "RiskLevel",
    "TOOL_NAME",
    "DEFAULT_TIMEOUT_SECONDS",
    "DEFAULT_CLOCK",
    "coerce_action",
    "new_result",
]
