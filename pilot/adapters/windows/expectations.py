"""Post-condition verification (Manus finding: input is never proof of completion).

Delivering a keystroke proves a keystroke was delivered. It does not prove the
application processed it, acted on it, or finished acting on it. Every
input-based operation in this lane therefore reports two distinct things:

* whether the input was **dispatched** (always known), and
* whether the intended end state **arrived** (known only when the caller said
  what to expect).

An :class:`Expectation` is how the caller says what to expect. When none is
supplied the operation still succeeds — refusing to type without a declared
post-condition would make the adapter unusable — but the Result carries
``completion_verified: false``, so nothing downstream can mistake "we pressed
the key" for "the thing happened".

Expectations are polled until they hold or the action's deadline expires,
because UI settles asynchronously and a single immediate check would mostly
measure timing luck.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .control_selectors import Selector, find_all, resolve
from .errors import CompletionUnverified, ElementNotFound, InvalidArguments
from .model import ElementSnapshot


@dataclass(frozen=True)
class Expectation:
    """A declared post-condition for an interaction."""

    #: An element that must exist after the action.
    selector: Selector | None = None
    #: When set, that element's value must match.
    value: str | None = None
    value_match: str = "exact"
    #: When True, ``selector`` must match *nothing* — for dialogs that should
    #: have closed, controls that should have disappeared.
    absent: bool = False
    #: A window with this title must exist afterwards. Also declares an
    #: expected modal, so the unexpected-modal guard lets it through.
    window_title: str | None = None
    #: No window with this title may exist afterwards.
    window_absent: str | None = None

    @property
    def is_empty(self) -> bool:
        return not any([self.selector, self.window_title, self.window_absent])

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any] | "Expectation" | None) -> "Expectation | None":
        if raw is None:
            return None
        if isinstance(raw, Expectation):
            return raw
        if not isinstance(raw, Mapping):
            raise InvalidArguments(
                "expect must be an object",
                details={"received_type": type(raw).__name__},
            )
        unknown = set(raw) - {"selector", "value", "value_match", "absent",
                              "window_title", "window_absent"}
        if unknown:
            raise InvalidArguments(
                f"unknown expect keys: {sorted(unknown)}",
                details={"unknown_keys": sorted(unknown)},
            )
        selector = raw.get("selector")
        expectation = cls(
            selector=Selector.from_mapping(selector) if selector else None,
            value=raw.get("value"),
            value_match=raw.get("value_match", "exact"),
            absent=bool(raw.get("absent", False)),
            window_title=raw.get("window_title"),
            window_absent=raw.get("window_absent"),
        )
        if expectation.is_empty:
            raise InvalidArguments(
                "expect must declare at least one of: selector, window_title, "
                "window_absent",
                details={"expect": dict(raw)},
            )
        if expectation.value is not None and expectation.selector is None:
            raise InvalidArguments(
                "expect.value requires expect.selector",
                details={"expect": dict(raw)},
            )
        if expectation.absent and expectation.value is not None:
            raise InvalidArguments(
                "expect.absent and expect.value are contradictory",
                details={"expect": dict(raw)},
            )
        return expectation

    def to_dict(self) -> dict[str, Any]:
        return {
            "selector": self.selector.to_dict() if self.selector else None,
            "value": self.value,
            "value_match": self.value_match,
            "absent": self.absent,
            "window_title": self.window_title,
            "window_absent": self.window_absent,
        }

    def expected_window_titles(self) -> tuple[str, ...]:
        """Window titles this expectation declares, for the modal guard."""
        return (self.window_title,) if self.window_title else ()


@dataclass
class ExpectationOutcome:
    """Result of evaluating an expectation."""

    satisfied: bool
    reason: str = ""
    observed: dict[str, Any] | None = None
    attempts: int = 0
    waited_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "satisfied": self.satisfied,
            "reason": self.reason,
            "observed": self.observed,
            "attempts": self.attempts,
            "waited_seconds": round(self.waited_seconds, 3),
        }


def _evaluate_once(expectation: Expectation, *, tree: ElementSnapshot | None,
                   window_titles: Sequence[str]) -> ExpectationOutcome:
    """One evaluation pass. No waiting, no I/O."""
    if expectation.window_title:
        wanted = expectation.window_title.casefold()
        if not any(wanted in (t or "").casefold() for t in window_titles):
            return ExpectationOutcome(
                False, f"no window titled {expectation.window_title!r} appeared",
                observed={"window_titles": list(window_titles)})

    if expectation.window_absent:
        unwanted = expectation.window_absent.casefold()
        still_there = [t for t in window_titles if unwanted in (t or "").casefold()]
        if still_there:
            return ExpectationOutcome(
                False,
                f"window {expectation.window_absent!r} was still present",
                observed={"matching_windows": still_there})

    if expectation.selector is None:
        return ExpectationOutcome(True, "window expectation satisfied")

    if tree is None:
        return ExpectationOutcome(False, "no control tree available to check",
                                  observed=None)

    matches = find_all(tree, expectation.selector)
    if expectation.absent:
        if matches:
            return ExpectationOutcome(
                False,
                f"{len(matches)} element(s) still matched a selector expected "
                "to be absent",
                observed={"match_count": len(matches),
                          "first": matches[0].element.to_dict(include_children=False)})
        return ExpectationOutcome(True, "expected element is absent")

    if not matches:
        return ExpectationOutcome(False, "expected element did not appear",
                                  observed={"match_count": 0})

    if expectation.value is None:
        return ExpectationOutcome(
            True, "expected element is present",
            observed={"match_count": len(matches),
                      "element": matches[0].element.to_dict(include_children=False)})

    # Resolve strictly for a value check: comparing the value of an arbitrary
    # one of several matches would make the verification meaningless.
    try:
        resolution = resolve(tree, expectation.selector, require_unique=True)
    except ElementNotFound:
        return ExpectationOutcome(False, "expected element did not appear")
    element = resolution.element

    from .control_selectors import _text_matches

    actual = element.value or ""
    if _text_matches(actual, expectation.value, expectation.value_match):
        return ExpectationOutcome(
            True, "expected value observed",
            observed={"value": actual,
                      "element": element.to_dict(include_children=False)})
    return ExpectationOutcome(
        False,
        f"expected value {expectation.value!r} but observed {actual!r}",
        observed={"value": actual,
                  "element": element.to_dict(include_children=False)})


def verify(expectation: Expectation | None, *, backend: Any, deadline: Any,
           window_handle: int | None, poll_interval: float = 0.2,
           context: str = "") -> ExpectationOutcome:
    """Poll until ``expectation`` holds or the deadline expires.

    Returns an unsatisfied outcome rather than raising, so the caller decides
    whether an unmet expectation is fatal for that operation. Raising here
    would rob the caller of the chance to attach it to evidence first.
    """
    if expectation is None:
        return ExpectationOutcome(True, "no expectation declared", attempts=0)

    started = deadline.elapsed
    attempts = 0
    outcome = ExpectationOutcome(False, "not evaluated")
    while True:
        attempts += 1
        try:
            titles = [w.title for w in backend.list_windows(visible_only=True)]
        except Exception:
            titles = []
        tree = None
        if expectation.selector is not None:
            try:
                tree = backend.control_tree(window_handle=window_handle)
            except Exception as exc:
                outcome = ExpectationOutcome(
                    False, f"could not read control tree: {type(exc).__name__}: {exc}")
                tree = None
        if tree is not None or expectation.selector is None:
            outcome = _evaluate_once(expectation, tree=tree, window_titles=titles)
        outcome.attempts = attempts
        outcome.waited_seconds = deadline.elapsed - started
        if outcome.satisfied or deadline.expired:
            return outcome
        backend.sleep(min(poll_interval, max(0.0, deadline.remaining)))


def require(outcome: ExpectationOutcome, expectation: Expectation | None,
            *, context: str) -> None:
    """Raise when a declared expectation was not met."""
    if expectation is None or outcome.satisfied:
        return
    raise CompletionUnverified(
        f"input was dispatched for {context} but the declared post-condition "
        f"was not met: {outcome.reason}",
        details={
            "expectation": expectation.to_dict(),
            "outcome": outcome.to_dict(),
            "note": "the input was delivered; whether the application acted on "
                    "it is unknown. Re-discover state before any retry.",
        },
    )


__all__ = ["Expectation", "ExpectationOutcome", "verify", "require"]
