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
    #: Ancestry scope. When set, only descendants of the element matching this
    #: (nested) selector are considered. This is the "scoped ancestry" half of
    #: the resolution rule: "the Save button *in the Save As dialog*" is a
    #: different question from "any Save button on the desktop", and without a
    #: scope the two are indistinguishable.
    within: "Selector | None" = None
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
            "enabled_only", "onscreen_only", "focusable_only", "max_depth",
            "index", "within",
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
            within=(cls.from_mapping(raw["within"])
                    if raw.get("within") is not None else None),
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
            "within": self.within.to_dict() if self.within else None,
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


#: Resolution tiers, strongest identification first. The ordering *is* the
#: "AutomationId first, exact role/name second" rule — it is applied, not
#: merely documented, and the tier that fired is recorded in evidence so a
#: mission log shows how weakly a control was identified.
TIER_AUTOMATION_ID = "automation_id"
TIER_EXACT_ROLE_NAME = "exact_role_name"
TIER_RELAXED_NAME = "relaxed_name"
TIER_STRUCTURAL = "structural"

#: Strongest to weakest. ``min_tier`` is checked against this order.
TIER_ORDER = (TIER_AUTOMATION_ID, TIER_EXACT_ROLE_NAME,
              TIER_RELAXED_NAME, TIER_STRUCTURAL)

_EXACT_NAME_MODES = {MatchMode.EXACT, MatchMode.IEQUALS}


@dataclass(frozen=True)
class Resolution:
    """A resolved element plus how confidently it was identified."""

    element: ElementSnapshot
    tier: str
    #: Every element that matched at the winning tier. Length 1 unless the
    #: caller explicitly opted out of uniqueness or used ``index``.
    candidates: tuple[ElementSnapshot, ...] = ()
    #: Non-fatal observations, e.g. an automation-id hit whose name differs
    #: from what the planner expected.
    warnings: tuple[str, ...] = ()
    #: Ancestry scope actually used, if ``within`` was supplied.
    scope: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "tier": self.tier,
            "candidate_count": len(self.candidates),
            "warnings": list(self.warnings),
            "scope": self.scope,
        }


def _construct(fields: dict[str, Any]) -> Selector:
    """Build a Selector bypassing the at-least-one-criterion check."""
    instance = object.__new__(Selector)
    for key in ("name", "name_match", "role", "automation_id", "class_name",
                "value", "value_match", "requires_patterns", "enabled_only",
                "onscreen_only", "focusable_only", "max_depth", "index", "within"):
        object.__setattr__(instance, key, fields.get(key))
    if instance.requires_patterns is None:
        object.__setattr__(instance, "requires_patterns", ())
    else:
        object.__setattr__(instance, "requires_patterns",
                           tuple(instance.requires_patterns))
    return instance


def build_tiers(selector: Selector) -> list[tuple[str, Selector]]:
    """Decompose a selector into ordered resolution attempts.

    Structural criteria (role, class, patterns, state filters, value) apply at
    every tier; only the *identifying* criterion changes. When a selector
    carries both an automation id and a name, the name tier remains as a
    fallback — an app whose automation ids change should degrade to name
    matching visibly rather than failing outright.
    """
    base: dict[str, Any] = selector.to_dict()
    base["role"] = selector.role
    base["requires_patterns"] = selector.requires_patterns
    base["within"] = selector.within
    base["name"] = None
    base["automation_id"] = None

    tiers: list[tuple[str, Selector]] = []
    if selector.automation_id is not None:
        tiers.append((TIER_AUTOMATION_ID,
                      _construct({**base, "automation_id": selector.automation_id})))
    if selector.name is not None:
        tier = (TIER_EXACT_ROLE_NAME if selector.name_match in _EXACT_NAME_MODES
                else TIER_RELAXED_NAME)
        tiers.append((tier, _construct({**base, "name": selector.name,
                                        "name_match": selector.name_match})))
    if not tiers:
        # No identifying criterion: role / class / pattern only. Legitimate
        # when it resolves uniquely (Notepad's single Document control), and
        # rejected below when it does not.
        tiers.append((TIER_STRUCTURAL, _construct(base)))
    return tiers


def _dedupe(matches: list[Match]) -> list[Match]:
    """Collapse duplicates that overlapping ancestry scopes can produce."""
    seen: set[str] = set()
    unique: list[Match] = []
    for match in matches:
        if match.element.runtime_id in seen:
            continue
        seen.add(match.element.runtime_id)
        unique.append(match)
    return unique


def _scope_roots(root: ElementSnapshot, selector: Selector,
                 *, require_unique: bool) -> tuple[list[ElementSnapshot], str]:
    """Resolve ``selector.within`` to the subtrees to search."""
    if selector.within is None:
        return [root], ""
    scope = resolve(root, selector.within, require_unique=require_unique)
    return [scope.element], scope.element.describe()


def resolve(root: ElementSnapshot, selector: Selector, *,
            require_unique: bool = True,
            min_tier: str | None = None) -> Resolution:
    """Resolve ``selector`` to exactly one element, tier by tier.

    Tiers are tried strongest-first. The *first tier that matches anything*
    decides the outcome: if it matched more than one element, that is an
    ambiguity to report, not a field to break with a tie-breaker. Falling
    through to a weaker tier because a stronger one was ambiguous would defeat
    the point of ordering them.

    ``require_unique`` defaults to **True**. Silently acting on the
    highest-scoring of several indistinguishable controls is how automation
    clicks the wrong button, so the caller must opt *out* of safety rather
    than into it.

    ``min_tier`` refuses identification weaker than the named tier — pass
    ``"automation_id"`` to forbid a silent fallback to name matching.
    """
    if min_tier is not None and min_tier not in TIER_ORDER:
        raise InvalidArguments(
            f"unknown min_tier {min_tier!r}",
            details={"min_tier": min_tier, "supported": list(TIER_ORDER)},
        )

    scopes, scope_description = _scope_roots(root, selector,
                                             require_unique=require_unique)
    tiers = build_tiers(selector)
    allowed = TIER_ORDER[:TIER_ORDER.index(min_tier) + 1] if min_tier else TIER_ORDER

    attempted: list[dict[str, Any]] = []
    for tier_name, tier_selector in tiers:
        if tier_name not in allowed:
            attempted.append({"tier": tier_name, "skipped": "weaker than min_tier"})
            continue
        matches = _dedupe([m for scope in scopes
                           for m in find_all(scope, tier_selector)])
        attempted.append({"tier": tier_name, "match_count": len(matches)})
        if not matches:
            continue

        if selector.index is not None:
            ordered = sorted(matches, key=lambda m: m.order)
            if selector.index >= len(ordered):
                raise ElementNotFound(
                    f"selector index {selector.index} out of range "
                    f"({len(ordered)} match(es) at tier {tier_name!r})",
                    details={"selector": selector.to_dict(),
                             "tier": tier_name, "match_count": len(ordered)},
                )
            return Resolution(element=ordered[selector.index].element,
                              tier=tier_name,
                              candidates=tuple(m.element for m in ordered),
                              warnings=("index used: ranking bypassed",),
                              scope=scope_description)

        if len(matches) > 1 and require_unique:
            raise AmbiguousSelector(
                f"{len(matches)} elements matched {selector.describe()} at "
                f"tier {tier_name!r}; refusing to guess",
                details={
                    "selector": selector.to_dict(),
                    "tier": tier_name,
                    "match_count": len(matches),
                    "candidates": [m.element.to_dict(include_children=False)
                                   for m in matches[:10]],
                    "hint": "add automation_id, a `within` ancestry scope, "
                            "or an explicit index to disambiguate",
                },
            )

        warnings: list[str] = []
        if (tier_name == TIER_AUTOMATION_ID and selector.name is not None
                and (matches[0].element.name or "") != selector.name):
            # The id matched but the label did not. Usually harmless
            # (localisation), occasionally the sign of a reused id.
            warnings.append(
                f"automation_id matched but name is "
                f"{matches[0].element.name!r}, expected {selector.name!r}")
        if tier_name != TIER_AUTOMATION_ID and selector.automation_id is not None:
            warnings.append(
                f"fell back to {tier_name!r}: automation_id "
                f"{selector.automation_id!r} not found")
        if tier_name in (TIER_RELAXED_NAME, TIER_STRUCTURAL):
            warnings.append(
                f"weak identification ({tier_name}): no automation id or "
                "exact name was used")
        if len(matches) > 1:
            warnings.append(
                f"{len(matches)} candidates matched; uniqueness was not required")

        return Resolution(element=matches[0].element, tier=tier_name,
                          candidates=tuple(m.element for m in matches),
                          warnings=tuple(warnings), scope=scope_description)

    raise ElementNotFound(
        f"no element matched {selector.describe()}",
        details={
            "selector": selector.to_dict(),
            "searched_elements": sum(len(list(scope.walk())) for scope in scopes),
            "tiers_attempted": attempted,
            "scope": scope_description,
            "near_misses": _near_misses(scopes[0], selector),
        },
    )


def resolve_one(root: ElementSnapshot, selector: Selector, *,
                require_unique: bool = True,
                min_tier: str | None = None) -> ElementSnapshot:
    """:func:`resolve`, returning only the element."""
    return resolve(root, selector, require_unique=require_unique,
                   min_tier=min_tier).element


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


__all__ = [
    "Selector", "MatchMode", "Match", "Resolution",
    "find_all", "resolve", "resolve_one", "build_tiers",
    "TIER_AUTOMATION_ID", "TIER_EXACT_ROLE_NAME", "TIER_RELAXED_NAME",
    "TIER_STRUCTURAL", "TIER_ORDER",
]
