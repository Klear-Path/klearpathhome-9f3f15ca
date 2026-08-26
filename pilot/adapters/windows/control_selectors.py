"""Semantic control selection (lane goal 6).

A :class:`Selector` describes *what* the planner wants by meaning — name,
role, automation id — never by pixel position. This module contains no I/O:
it takes a already-captured :class:`~.model.ElementSnapshot` tree and returns
matches, which makes control-finding exhaustively unit-testable.

Ranking matters as much as matching. Real UI trees contain many elements whose
name matches loosely, so candidates are scored and the caller can insist on an
unambiguous winner (see :func:`resolve_one`).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .errors import AmbiguousSelector, ElementNotFound, InvalidArguments
from .model import ElementSnapshot, normalize_role


class MatchMode(str):
    """String-enum of the supported text comparison modes."""

    EXACT = "exact"
    IEQUALS = "iequals"
    CONTAINS = "contains"
    STARTSWITH = "startswith"
    REGEX = "regex"


_VALID_MODES = {
    MatchMode.EXACT,
    MatchMode.IEQUALS,
    MatchMode.CONTAINS,
    MatchMode.STARTSWITH,
    MatchMode.REGEX,
}

#: Score contributions. Automation id outranks name because it is the
#: developer-assigned stable handle, whereas names are localised and reused.
_SCORE_AUTOMATION_ID = 100
_SCORE_NAME_EXACT = 60
_SCORE_NAME_IEQUALS = 50
_SCORE_NAME_PREFIX = 30
_SCORE_NAME_CONTAINS = 20
_SCORE_NAME_REGEX = 40
_SCORE_ROLE = 15
_SCORE_CLASS = 10
_SCORE_PATTERN = 8
_SCORE_INTERACTABLE = 5
_SCORE_FOCUSABLE = 2


def _text_matches(candidate: str, wanted: str, mode: str) -> bool:
    if mode == MatchMode.EXACT:
        return candidate == wanted
    if mode == MatchMode.IEQUALS:
        return candidate.casefold() == wanted.casefold()
    if mode == MatchMode.CONTAINS:
        return wanted.casefold() in candidate.casefold()
    if mode == MatchMode.STARTSWITH:
        return candidate.casefold().startswith(wanted.casefold())
    if mode == MatchMode.REGEX:
        import re

        try:
            return re.search(wanted, candidate) is not None
        except re.error as exc:
            raise InvalidArguments(
                f"invalid regex in selector: {exc}", details={"pattern": wanted}
            ) from exc
    raise InvalidArguments(
        f"unknown match mode {mode!r}",
        details={"mode": mode, "supported": sorted(_VALID_MODES)},
    )


@dataclass(frozen=True)
class Selector:
    """Declarative description of a target element.

    All supplied criteria must match (AND semantics). ``name`` is compared
    against both the accessible name and, for value-bearing controls, nothing
    else — value matching is a separate criterion so that "find the edit whose
    text is X" and "find the control labelled X" stay distinguishable.
    """

    name: str | None = None
    name_match: str = MatchMode.IEQUALS
    role: str | None = None
    automation_id: str | None = None
    class_name: str | None = None
    value: str | None = None
    value_match: str = MatchMode.CONTAINS
    requires_patterns: tuple[str, ...] = ()
    enabled_only: bool = True
    onscreen_only: bool = True
    focusable_only: bool = False
    max_depth: int | None = None
    #: When set, pick the Nth match in document order instead of the best-scoring
    #: one. An explicit escape hatch for genuinely repeated controls; using it
    #: means giving up ranking, so it is never the default.
    index: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "role", normalize_role(self.role) or None)
        for field_name in ("name_match", "value_match"):
            mode = getattr(self, field_name)
            if mode not in _VALID_MODES:
                raise InvalidArguments(
                    f"unknown {field_name} {mode!r}",
                    details={"mode": mode, "supported": sorted(_VALID_MODES)},
                )
        if not self.criteria_present:
            raise InvalidArguments(
                "selector must constrain at least one of: name, role, "
                "automation_id, class_name, value, requires_patterns",
                details={"selector": self.to_dict()},
            )
        if self.index is not None and self.index < 0:
            raise InvalidArguments(
                "selector index must be >= 0", details={"index": self.index}
            )

    @property
    def criteria_present(self) -> bool:
        return any([
            self.name, self.role, self.automation_id,
            self.class_name, self.value, self.requires_patterns,
        ])

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any] | "Selector" | None) -> "Selector":
        """Build a Selector from planner-supplied JSON-ish arguments."""
        if isinstance(raw, Selector):
            return raw
        if not raw:
            raise InvalidArguments("a selector is required", details={"selector": raw})
        if not isinstance(raw, Mapping):
            raise InvalidArguments(
                "selector must be an object",
                details={"received_type": type(raw).__name__},
            )
        unknown = set(raw) - {
            "name", "name_match", "role", "control_type", "automation_id",
            "class_name", "value", "value_match", "requires_patterns",
            "enabled_only", "onscreen_only", "focusable_only", "max_depth", "index",
        }
        if unknown:
            raise InvalidArguments(
                f"unknown selector keys: {sorted(unknown)}",
                details={"unknown_keys": sorted(unknown)},
            )
        patterns = raw.get("requires_patterns") or ()
        if isinstance(patterns, str):
            patterns = (patterns,)
        return cls(
            name=raw.get("name"),
            name_match=raw.get("name_match", MatchMode.IEQUALS),
            # `control_type` is accepted as an alias because that is UIA's own
            # vocabulary and planners tend to reach for it.
            role=raw.get("role") or raw.get("control_type"),
            automation_id=raw.get("automation_id"),
            class_name=raw.get("class_name"),
            value=raw.get("value"),
            value_match=raw.get("value_match", MatchMode.CONTAINS),
            requires_patterns=tuple(patterns),
            enabled_only=bool(raw.get("enabled_only", True)),
            onscreen_only=bool(raw.get("onscreen_only", True)),
            focusable_only=bool(raw.get("focusable_only", False)),
            max_depth=raw.get("max_depth"),
            index=raw.get("index"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "name_match": self.name_match,
            "role": self.role,
            "automation_id": self.automation_id,
            "class_name": self.class_name,
            "value": self.value,
            "value_match": self.value_match,
            "requires_patterns": list(self.requires_patterns),
            "enabled_only": self.enabled_only,
            "onscreen_only": self.onscreen_only,
            "focusable_only": self.focusable_only,
            "max_depth": self.max_depth,
            "index": self.index,
        }

    def describe(self) -> str:
        parts = [f"{k}={v!r}" for k, v in self.to_dict().items()
                 if v not in (None, (), [], "")]
        return "Selector(" + ", ".join(parts) + ")"

    # --- matching -------------------------------------------------------

    def matches(self, element: ElementSnapshot) -> bool:
        if self.max_depth is not None and element.depth > self.max_depth:
            return False
        if self.enabled_only and not element.enabled:
            return False
        if self.onscreen_only and element.offscreen:
            return False
        if self.focusable_only and not element.keyboard_focusable:
            return False
        if self.role and element.role != self.role:
            return False
        if self.automation_id is not None and element.automation_id != self.automation_id:
            return False
        if self.class_name is not None and element.class_name != self.class_name:
            return False
        if self.name is not None and not _text_matches(element.name or "", self.name, self.name_match):
            return False
        if self.value is not None and not _text_matches(element.value or "", self.value, self.value_match):
            return False
        for pattern in self.requires_patterns:
            if not element.supports(pattern):
                return False
        return True

    def score(self, element: ElementSnapshot) -> int:
        """Rank a matching element. Higher is a better fit."""
        total = 0
        if self.automation_id is not None:
            total += _SCORE_AUTOMATION_ID
        if self.name is not None:
            name = element.name or ""
            if name == self.name:
                total += _SCORE_NAME_EXACT
            elif name.casefold() == self.name.casefold():
                total += _SCORE_NAME_IEQUALS
            elif self.name_match == MatchMode.REGEX:
                total += _SCORE_NAME_REGEX
            elif name.casefold().startswith(self.name.casefold()):
                total += _SCORE_NAME_PREFIX
            else:
                total += _SCORE_NAME_CONTAINS
        if self.role:
            total += _SCORE_ROLE
        if self.class_name is not None:
            total += _SCORE_CLASS
        total += _SCORE_PATTERN * len(self.requires_patterns)
        if element.interactable:
            total += _SCORE_INTERACTABLE
        if element.keyboard_focusable:
            total += _SCORE_FOCUSABLE
        # Prefer shallower elements: a matching container is usually the label
        # wrapper, and the actionable control tends to sit nearer the surface
        # the planner was describing. Small weight so it only breaks ties.
        total -= element.depth
        return total


@dataclass(frozen=True)
class Match:
    """A scored selector hit, retaining document order for stable tie-breaks."""

    element: ElementSnapshot
    score: int
    order: int


def find_all(root: ElementSnapshot, selector: Selector) -> list[Match]:
    """Every element matching ``selector``, best-scoring first.

    Ties break on document order so results are deterministic for a given
    tree — a hard requirement for reproducible missions.
    """
    matches: list[Match] = []
    for order, element in enumerate(root.walk()):
        if selector.matches(element):
            matches.append(Match(element=element, score=selector.score(element), order=order))
    if selector.index is not None:
        matches.sort(key=lambda m: m.order)
        return matches
    matches.sort(key=lambda m: (-m.score, m.order))
    return matches


def resolve_one(root: ElementSnapshot, selector: Selector, *,
                require_unique: bool = False) -> ElementSnapshot:
    """Resolve ``selector`` to exactly one element.

    Raises :class:`ElementNotFound` when nothing matches. With
    ``require_unique`` the caller refuses to guess: any tie at the top score
    raises :class:`AmbiguousSelector` listing the candidates, so a planner can
    disambiguate instead of silently acting on the wrong control.
    """
    matches = find_all(root, selector)
    if not matches:
        raise ElementNotFound(
            f"no element matched {selector.describe()}",
            details={
                "selector": selector.to_dict(),
                "searched_elements": sum(1 for _ in root.walk()),
                "near_misses": _near_misses(root, selector),
            },
        )
    if selector.index is not None:
        if selector.index >= len(matches):
            raise ElementNotFound(
                f"selector index {selector.index} out of range "
                f"({len(matches)} match(es))",
                details={"selector": selector.to_dict(), "match_count": len(matches)},
            )
        return matches[selector.index].element
    if require_unique and len(matches) > 1 and matches[0].score == matches[1].score:
        tied = [m for m in matches if m.score == matches[0].score]
        raise AmbiguousSelector(
            f"{len(tied)} elements tied for {selector.describe()}",
            details={
                "selector": selector.to_dict(),
                "candidates": [m.element.to_dict(include_children=False) for m in tied[:10]],
                "hint": "add automation_id, role, or index to disambiguate",
            },
        )
    return matches[0].element


def _near_misses(root: ElementSnapshot, selector: Selector, *, limit: int = 5) -> list[dict[str, Any]]:
    """Elements that matched the *name* but failed another criterion.

    Purely diagnostic, and worth the cost: "found it but it was disabled" and
    "no such control" look identical to a planner otherwise, and they call for
    completely different recovery.
    """
    if selector.name is None:
        return []
    loose = Selector(
        name=selector.name,
        name_match=MatchMode.CONTAINS,
        enabled_only=False,
        onscreen_only=False,
    )
    out: list[dict[str, Any]] = []
    for element in root.walk():
        if len(out) >= limit:
            break
        if loose.matches(element) and not selector.matches(element):
            reasons = []
            if selector.role and element.role != selector.role:
                reasons.append(f"role is {element.role!r}, wanted {selector.role!r}")
            if selector.enabled_only and not element.enabled:
                reasons.append("disabled")
            if selector.onscreen_only and element.offscreen:
                reasons.append("offscreen")
            if selector.focusable_only and not element.keyboard_focusable:
                reasons.append("not keyboard focusable")
            missing = [p for p in selector.requires_patterns if not element.supports(p)]
            if missing:
                reasons.append(f"missing patterns {missing}")
            if (selector.automation_id is not None
                    and element.automation_id != selector.automation_id):
                reasons.append(f"automation_id is {element.automation_id!r}")
            out.append({
                "element": element.describe(),
                "runtime_id": element.runtime_id,
                "reasons": reasons or ["name matched only loosely"],
            })
    return out


__all__ = ["Selector", "MatchMode", "Match", "find_all", "resolve_one"]
