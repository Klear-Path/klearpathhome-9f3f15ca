"""Operation registry: the adapter's verb vocabulary.

Each entry declares its handler, the evidence to capture around it, and the
backend capabilities it needs. Registration is table-driven so adding a verb
(or a vision-assisted variant of one) touches one place.

Handlers are written against :class:`~.backend.UiaBackend`, never against
Windows APIs, so every branch below is reachable from the unit suite.

Timeouts: ``Action.timeout_seconds`` is enforced cooperatively via
:class:`Deadline`. Polling handlers check it between attempts. A single
blocking backend call cannot be preempted from here — that bound belongs to
the backend — so the deadline is a floor on responsiveness, not a hard kill.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

from .contracts import Action
from . import expectations, guards
from .errors import (
    ElementNotFound,
    ElementNotInteractable,
    InvalidArguments,
    LaunchFailed,
    StaleElement,
    TimeoutExpired,
    UnsupportedOperation,
    UnsupportedUi,
    VerificationFailed,
    WindowNotFound,
)
from .redaction import (
    redact_element_payload,
    redact_text,
    redact_tree_rows,
)
from .evidence import CapturePolicy
from .keyboard import describe_keys, parse_keys
from .model import (
    PATTERN_EXPAND_COLLAPSE,
    PATTERN_INVOKE,
    PATTERN_LEGACY_IACCESSIBLE,
    PATTERN_SELECTION_ITEM,
    PATTERN_TOGGLE,
    PATTERN_VALUE,
    ElementSnapshot,
    WindowInfo,
    describe_tree_stats,
    summarize_tree,
)
from .control_selectors import Selector, find_all, resolve, resolve_one


class Deadline:
    """Cooperative timeout tracker."""

    def __init__(self, seconds: float, *, now: Callable[[], float] = time.monotonic) -> None:
        self._now = now
        self.seconds = seconds
        self.started = now()

    @property
    def elapsed(self) -> float:
        return self._now() - self.started

    @property
    def remaining(self) -> float:
        return max(0.0, self.seconds - self.elapsed)

    @property
    def expired(self) -> bool:
        return self.remaining <= 0.0

    def check(self, what: str) -> None:
        if self.expired:
            raise TimeoutExpired(
                f"timed out after {self.seconds:g}s while {what}",
                details={"timeout_seconds": self.seconds, "elapsed_seconds": round(self.elapsed, 3)},
            )


@dataclass
class OperationContext:
    """Everything a handler is allowed to touch."""

    action: Action
    backend: Any
    deadline: Deadline
    #: Window the operation resolved to, if any. Drives evidence scoping so
    #: "after" state is captured from the same window as "before".
    window_handle: int | None = None
    #: Desktop state observed before the handler ran. Set by the adapter so
    #: the modal and foreground guards have a baseline to compare against.
    desktop_before: guards.DesktopSnapshot | None = None
    #: Filled in by the guards, merged into Result.evidence.
    guard_records: dict[str, Any] = field(default_factory=dict)

    def arg(self, name: str, default: Any = None) -> Any:
        return self.action.arg(name, default)

    def require(self, name: str) -> Any:
        return self.action.require(name)


@dataclass
class OperationOutcome:
    """What a handler produces, before the adapter wraps it in a Result."""

    stdout: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)
    window_handle: int | None = None
    #: Screenshot paths a handler captured itself (over and above policy).
    screenshots: list[str] = field(default_factory=list)


Handler = Callable[[OperationContext], OperationOutcome]


@dataclass(frozen=True)
class OperationSpec:
    name: str
    handler: Handler
    description: str
    before: CapturePolicy = field(default_factory=CapturePolicy.minimal)
    after: CapturePolicy = field(default_factory=CapturePolicy.minimal)
    #: Attribute names on :class:`~.backend.BackendCapabilities` that must be
    #: true. Checked before the handler runs.
    requires: tuple[str, ...] = ()
    read_only: bool = False
    #: Whether repeating this operation with identical arguments is safe once
    #: it may already have partially applied. Discovery is idempotent;
    #: ``set_text`` is (same value, same end state); dispatching input and
    #: invoking a control are **not** — a second Invoke on a Send button sends
    #: twice. Drives the ``retryable`` the adapter actually reports.
    idempotent: bool = True
    #: Whether this operation synthesises input, and so needs the
    #: foreground-identity guard around it.
    synthesises_input: bool = False


REGISTRY: dict[str, OperationSpec] = {}


def register(spec: OperationSpec) -> OperationSpec:
    if spec.name in REGISTRY:
        raise RuntimeError(f"operation {spec.name!r} is already registered")
    REGISTRY[spec.name] = spec
    return spec


def get(name: str) -> OperationSpec:
    try:
        return REGISTRY[name]
    except KeyError:
        raise UnsupportedOperation(
            f"unknown operation {name!r}",
            details={"operation": name, "supported": sorted(REGISTRY)},
        ) from None


# ==========================================================================
# Shared helpers
# ==========================================================================

def _match_window(windows: Sequence[WindowInfo], *, handle: int | None,
                  title: str | None, title_match: str,
                  process_name: str | None) -> WindowInfo:
    """Locate one window by handle, title, or owning process."""
    if handle is not None:
        for window in windows:
            if window.handle == int(handle):
                return window
        raise WindowNotFound(
            f"no window with handle {handle}",
            details={"handle": handle, "available": [w.to_dict() for w in windows[:20]]},
        )

    candidates = list(windows)
    if process_name:
        wanted = process_name.casefold()
        # Accept "notepad" for "notepad.exe": planners name applications, not
        # executables.
        candidates = [
            w for w in candidates
            if w.process_name.casefold() == wanted
            or w.process_name.casefold() == f"{wanted}.exe"
            or w.process_name.casefold().removesuffix(".exe") == wanted.removesuffix(".exe")
        ]
    if title:
        from .control_selectors import _text_matches

        candidates = [w for w in candidates if _text_matches(w.title or "", title, title_match)]

    if not candidates:
        raise WindowNotFound(
            "no window matched the request",
            details={
                "title": title, "title_match": title_match,
                "process_name": process_name,
                "available": [w.to_dict() for w in windows[:20]],
            },
        )
    # Prefer a visible, non-minimised, foreground-ish window; then the one with
    # the largest area, which in practice is the real application window rather
    # than a hidden helper window sharing the title.
    candidates.sort(key=lambda w: (
        not w.is_visible,
        w.is_minimized,
        not w.is_foreground,
        -(w.rect.width * w.rect.height),
    ))
    return candidates[0]


def _resolve_window(ctx: OperationContext, *, required: bool) -> WindowInfo | None:
    """Determine which window an operation applies to.

    Precedence: explicit handle > title/process match > current foreground.
    Falling back to the foreground window is what makes short action sequences
    ("type this, now save") read naturally.
    """
    handle = ctx.arg("window_handle")
    title = ctx.arg("window_title")
    process_name = ctx.arg("process_name")
    title_match = ctx.arg("window_title_match", "contains")

    if handle is None and title is None and process_name is None:
        foreground = ctx.backend.foreground_window()
        if foreground is None and required:
            raise WindowNotFound(
                "no window specified and nothing holds foreground focus",
                details={"hint": "pass window_handle, window_title, or process_name"},
            )
        return foreground

    windows = ctx.backend.list_windows(visible_only=False)
    return _match_window(
        windows, handle=handle, title=title,
        title_match=title_match, process_name=process_name,
    )


def _selector_from(ctx: OperationContext, key: str = "selector") -> Selector:
    raw = ctx.arg(key)
    if raw is None:
        # Allow the common criteria to be passed flat, which keeps simple
        # actions readable: {"name": "Save", "role": "button"}.
        flat = {
            k: ctx.arg(k) for k in
            ("name", "name_match", "role", "control_type", "automation_id",
             "class_name", "value", "value_match", "index")
            if ctx.arg(k) is not None
        }
        if not flat:
            raise InvalidArguments(
                f"operation '{ctx.action.operation}' requires a '{key}' object "
                "or flat selector criteria (name / role / automation_id)",
                details={"operation": ctx.action.operation},
            )
        raw = flat
    return Selector.from_mapping(raw)


def _tree_for(ctx: OperationContext, window: WindowInfo | None) -> ElementSnapshot:
    return ctx.backend.control_tree(
        window_handle=window.handle if window else None,
        max_depth=int(ctx.arg("max_depth", 12)),
        max_elements=int(ctx.arg("max_elements", 2000)),
    )


def _find_element(ctx: OperationContext, *, require_patterns: Sequence[str] = (),
                  key: str = "selector"):
    """Resolve a selector to an element, retrying until the deadline.

    Returns ``(element, tree_root, window, resolution)``.

    Every attempt re-walks the control tree from scratch — state is
    re-discovered, never carried over from a previous attempt. That is what
    makes the polling safe: a cached tree would let the adapter act on an
    element that has since moved, been disabled, or been destroyed.

    ``require_unique`` defaults to **True**. An ambiguous semantic match is
    rejected rather than resolved by ranking, so the caller must opt out
    deliberately.
    """
    window = _resolve_window(ctx, required=False)
    selector = _selector_from(ctx, key)
    require_unique = bool(ctx.arg("require_unique", True))
    min_tier = ctx.arg("min_tier")
    poll = float(ctx.arg("poll_interval_seconds", 0.25))

    last_error: Exception | None = None
    attempts = 0
    while True:
        attempts += 1
        # Fresh walk each attempt: re-discover before acting.
        root = _tree_for(ctx, window)
        try:
            resolution = resolve(root, selector, require_unique=require_unique,
                                 min_tier=min_tier)
        except ElementNotFound as exc:
            last_error = exc
        else:
            _assert_usable(resolution.element, require_patterns, selector)
            ctx.guard_records["resolution"] = {
                **resolution.to_dict(), "attempts": attempts}
            return resolution.element, root, window, resolution

        if ctx.deadline.expired:
            # Surface the selector diagnosis, not a bare timeout: the near-miss
            # detail is the actionable part.
            assert last_error is not None
            raise last_error
        ctx.backend.sleep(min(poll, ctx.deadline.remaining))


def _assert_usable(element: ElementSnapshot, require_patterns: Sequence[str],
                   selector: Selector) -> None:
    """Reject an element we can see but demonstrably cannot drive (goal 13)."""
    if not element.enabled:
        raise ElementNotInteractable(
            f"element is disabled: {element.describe()}",
            details={"element": element.to_dict(include_children=False),
                     "selector": selector.to_dict()},
        )
    if element.offscreen:
        raise ElementNotInteractable(
            f"element is offscreen: {element.describe()}",
            details={"element": element.to_dict(include_children=False),
                     "selector": selector.to_dict()},
        )
    if require_patterns and not any(element.supports(p) for p in require_patterns):
        raise UnsupportedUi(
            f"element exposes no usable accessibility pattern for this "
            f"interaction: {element.describe()}",
            details={
                "element": element.to_dict(include_children=False),
                "required_any_of": list(require_patterns),
                "advertised_patterns": list(element.patterns),
                "fallback": "coordinate click via click_control, or vision backend",
            },
        )


def _expectation(ctx: OperationContext) -> "expectations.Expectation | None":
    return expectations.Expectation.from_mapping(ctx.arg("expect"))


def _guarded_input(ctx: OperationContext, dispatch, *, context: str,
                   window: WindowInfo | None) -> dict[str, Any]:
    """Run an input-dispatching callable inside the safety guards.

    The ordering matters and is the whole point:

    1. **Before**: refuse to act across an integrity boundary, or while a UAC
       prompt is up. Both are conditions no retry can clear, so they are
       caught before any input is synthesised rather than after.
    2. **Dispatch**: the actual keystroke / click.
    3. **After**: check foreground identity, then check for undeclared
       dialogs, then evaluate the declared post-condition.

    Failures raised after step 2 carry ``side_effect_possible``, because the
    input really was delivered — the adapter uses that to decide whether the
    action may be retried at all.
    """
    expectation = _expectation(ctx)
    allow_modals = bool(ctx.arg("allow_modals", False))
    before = ctx.desktop_before or guards.snapshot_desktop(ctx.backend)

    guards.check_uac(before)
    elevation = guards.check_elevation(ctx.backend, window or before.foreground)
    ctx.guard_records["elevation"] = elevation

    dispatch()

    settle = float(ctx.arg("settle_seconds", 0.1))
    if settle > 0:
        ctx.backend.sleep(settle)

    after = guards.snapshot_desktop(ctx.backend)
    guards.check_uac(after)

    try:
        ctx.guard_records["foreground"] = guards.check_foreground_stable(
            before, after, context=context)
    except Exception as exc:
        # Focus was stolen mid-input. The dispatch already happened, so this is
        # explicitly a side-effecting failure.
        setattr(exc, "side_effect_possible", True)
        raise

    expected_titles = expectation.expected_window_titles() if expectation else ()
    try:
        ctx.guard_records["modal"] = guards.check_no_unexpected_modal(
            before, after, expected_titles=expected_titles,
            allow_modals=allow_modals, context=context)
    except Exception as exc:
        setattr(exc, "side_effect_possible", True)
        raise

    outcome = expectations.verify(
        expectation, backend=ctx.backend, deadline=ctx.deadline,
        window_handle=window.handle if window else None,
        poll_interval=float(ctx.arg("poll_interval_seconds", 0.2)),
        context=context)
    expectations.require(outcome, expectation, context=context)

    # The load-bearing distinction: input was dispatched, and *separately*,
    # whether the intended end state was confirmed. Without a declared
    # expectation the second is simply unknown, and says so.
    record = {
        "input_dispatched": True,
        "completion_verified": bool(expectation) and outcome.satisfied,
        "expectation": expectation.to_dict() if expectation else None,
        "expectation_outcome": outcome.to_dict(),
    }
    if not expectation:
        record["completion_note"] = (
            "no post-condition was declared; input delivery is confirmed but "
            "the application's response is unverified. Pass `expect` to make "
            "completion checkable."
        )
    ctx.guard_records.update(record)
    return record


def _fresh_rect(ctx: OperationContext, element: ElementSnapshot):
    """Re-read an element's geometry immediately before a coordinate click.

    The rect captured during discovery is already stale by the time a decision
    has been made about it: the window may have moved, been resized, or
    changed monitor — and on a multi-monitor or mixed-DPI desktop the same
    logical control can sit at completely different physical coordinates from
    one moment to the next. Clicking remembered coordinates is how a fallback
    hits the wrong window.
    """
    try:
        current = ctx.backend.element_rect(element)
    except Exception as exc:
        raise StaleElement(
            f"could not re-read geometry for {element.describe()}: "
            f"{type(exc).__name__}: {exc}",
            details={"element": redact_element_payload(
                element.to_dict(include_children=False))},
        ) from exc

    if current is None or current.is_empty:
        raise UnsupportedUi(
            f"element has no clickable bounding rectangle at click time: "
            f"{element.describe()}",
            details={"element": redact_element_payload(
                element.to_dict(include_children=False)),
                     "discovered_rect": element.rect.to_dict(),
                     "current_rect": current.to_dict() if current else None},
        )

    moved = (abs(current.left - element.rect.left)
             + abs(current.top - element.rect.top))
    resized = (abs(current.width - element.rect.width)
               + abs(current.height - element.rect.height))
    tolerance = int(ctx.arg("geometry_tolerance_px", 0))
    record = {
        "discovered_rect": element.rect.to_dict(),
        "click_rect": current.to_dict(),
        "moved_px": moved,
        "resized_px": resized,
        "refreshed_before_click": True,
    }
    if tolerance and (moved > tolerance or resized > tolerance):
        raise StaleElement(
            f"element moved {moved}px and resized {resized}px between "
            f"discovery and click, exceeding the {tolerance}px tolerance",
            details={**record, "element": redact_element_payload(
                element.to_dict(include_children=False))},
        )
    ctx.guard_records["geometry"] = record
    return current


# ==========================================================================
# Handlers
# ==========================================================================

def _op_capabilities(ctx: OperationContext) -> OperationOutcome:
    caps = ctx.backend.capabilities()
    payload = caps.to_dict()
    return OperationOutcome(
        stdout=f"backend={payload.get('name')} platform={payload.get('platform')}",
        evidence={"capabilities": payload, "operations": sorted(REGISTRY)},
    )


def _op_list_windows(ctx: OperationContext) -> OperationOutcome:
    visible_only = bool(ctx.arg("visible_only", True))
    windows = ctx.backend.list_windows(visible_only=visible_only)
    title_filter = ctx.arg("title")
    if title_filter:
        from .control_selectors import _text_matches

        mode = ctx.arg("title_match", "contains")
        windows = [w for w in windows if _text_matches(w.title or "", title_filter, mode)]
    rows = [w.to_dict() for w in windows]
    return OperationOutcome(
        stdout=f"{len(rows)} window(s)",
        evidence={"windows": rows, "window_count": len(rows)},
    )


def _op_get_foreground_window(ctx: OperationContext) -> OperationOutcome:
    window = ctx.backend.foreground_window()
    if window is None:
        # Not an error: an unlocked-but-idle desktop genuinely has no
        # foreground window. Report the fact.
        return OperationOutcome(
            stdout="no foreground window",
            evidence={"foreground_window": None},
        )
    return OperationOutcome(
        stdout=f"foreground: {window.title!r} (pid {window.process_id})",
        evidence={"foreground_window": window.to_dict()},
        window_handle=window.handle,
    )


def _op_launch_application(ctx: OperationContext) -> OperationOutcome:
    command = ctx.require("command")
    if not isinstance(command, str) or not command.strip():
        raise InvalidArguments("command must be a non-empty string",
                              details={"command": command})
    raw_args = ctx.arg("arguments", ())
    if isinstance(raw_args, str):
        raise InvalidArguments(
            "arguments must be a list of strings, not a single string "
            "(shell splitting is deliberately not performed)",
            details={"arguments": raw_args},
        )
    arguments = tuple(str(a) for a in (raw_args or ()))
    wait_seconds = float(ctx.arg("wait_for_window_seconds",
                                 min(10.0, ctx.deadline.remaining)))

    try:
        process_id, window = ctx.backend.launch(
            command,
            arguments=arguments,
            working_directory=ctx.arg("working_directory"),
            wait_for_window_seconds=wait_seconds,
        )
    except FileNotFoundError as exc:
        raise LaunchFailed(
            f"executable not found: {command}",
            details={"command": command, "error": str(exc)},
        ) from exc

    if ctx.arg("require_window", True) and window is None:
        raise LaunchFailed(
            f"{command!r} started (pid {process_id}) but produced no top-level "
            f"window within {wait_seconds:g}s",
            details={"command": command, "process_id": process_id,
                     "wait_for_window_seconds": wait_seconds,
                     "hint": "pass require_window=false for windowless programs"},
        )

    return OperationOutcome(
        stdout=f"launched {command!r} pid={process_id}"
               + (f" window={window.title!r}" if window else " (no window)"),
        evidence={
            "process_id": process_id,
            "launched_command": command,
            "launched_arguments": list(arguments),
            "window": window.to_dict() if window else None,
        },
        window_handle=window.handle if window else None,
    )


def _op_focus_window(ctx: OperationContext) -> OperationOutcome:
    window = _resolve_window(ctx, required=True)
    assert window is not None
    before = window.to_dict()
    focused = ctx.backend.focus_window(window.handle)

    if not focused.is_foreground:
        # Windows can refuse a foreground change (SetForegroundWindow is
        # restricted). Report it as a real, retryable failure rather than
        # pretending focus succeeded and letting subsequent keystrokes land in
        # the wrong application — the worst possible outcome for this lane.
        raise ElementNotInteractable(
            f"window {focused.title!r} did not take foreground focus",
            details={"window": focused.to_dict(),
                     "hint": "another process may hold foreground lock; "
                             "retry or bring the desktop forward"},
        )

    return OperationOutcome(
        stdout=f"focused {focused.title!r}",
        evidence={"window_before": before, "window_after": focused.to_dict()},
        window_handle=focused.handle,
    )


def _op_get_control_tree(ctx: OperationContext) -> OperationOutcome:
    window = _resolve_window(ctx, required=False)
    root = _tree_for(ctx, window)
    stats = describe_tree_stats(root)
    limit = int(ctx.arg("limit", 60))
    include_full = bool(ctx.arg("include_full_tree", False))

    evidence: dict[str, Any] = {
        "window": window.to_dict() if window else None,
        "root": root.to_dict(include_children=False),
        "stats": stats,
        "elements": redact_tree_rows(summarize_tree(root, limit=limit)),
        "truncated": stats["total_elements"] > limit,
    }
    if include_full:
        evidence["full_tree"] = redact_element_payload(root.to_dict())

    if stats["interactable_elements"] == 0 and stats["total_elements"] <= 2:
        # A window whose entire tree is one opaque node is the classic
        # inaccessible surface (custom renderer, some Electron/game windows).
        # Flag it explicitly so the planner can escalate rather than retrying
        # selectors that will never match.
        evidence["accessibility_warning"] = (
            "window exposes no interactable UIA children; UI is likely "
            "custom-rendered and needs a vision fallback"
        )

    return OperationOutcome(
        stdout=f"{stats['total_elements']} element(s), "
               f"{stats['interactable_elements']} interactable",
        evidence=evidence,
        window_handle=window.handle if window else None,
    )


def _op_find_controls(ctx: OperationContext) -> OperationOutcome:
    window = _resolve_window(ctx, required=False)
    selector = _selector_from(ctx)
    root = _tree_for(ctx, window)
    matches = find_all(root, selector)
    limit = int(ctx.arg("limit", 20))
    rows = [
        {**redact_element_payload(m.element.to_dict(include_children=False)),
         "score": m.score, "order": m.order}
        for m in matches[:limit]
    ]
    return OperationOutcome(
        stdout=f"{len(matches)} match(es) for {selector.describe()}",
        evidence={
            "selector": selector.to_dict(),
            "match_count": len(matches),
            "matches": rows,
            "searched_elements": describe_tree_stats(root)["total_elements"],
        },
        window_handle=window.handle if window else None,
    )


def _op_get_element_state(ctx: OperationContext) -> OperationOutcome:
    element, root, window, resolution = _find_element(ctx)
    live = ctx.backend.refresh(element)
    payload = redact_element_payload(live.to_dict(include_children=False))
    return OperationOutcome(
        stdout=f"{live.describe()} value={payload.get('value')!r}",
        evidence={"element": payload, "resolution": resolution.to_dict()},
        window_handle=window.handle if window else None,
    )


def _op_wait_for_element(ctx: OperationContext) -> OperationOutcome:
    element, root, window, resolution = _find_element(ctx)
    return OperationOutcome(
        stdout=f"found {element.describe()} after {ctx.deadline.elapsed:.2f}s",
        evidence={"element": redact_element_payload(
                      element.to_dict(include_children=False)),
                  "resolution": resolution.to_dict(),
                  "waited_seconds": round(ctx.deadline.elapsed, 3)},
        window_handle=window.handle if window else None,
    )


def _op_invoke_control(ctx: OperationContext) -> OperationOutcome:
    element, root, window, resolution = _find_element(
        ctx, require_patterns=(PATTERN_INVOKE, PATTERN_SELECTION_ITEM,
                               PATTERN_TOGGLE, PATTERN_EXPAND_COLLAPSE,
                               PATTERN_LEGACY_IACCESSIBLE),
    )
    # Prefer the pattern that matches the element's own semantics rather than
    # forcing Invoke on everything: invoking a list item is a no-op on some
    # providers, whereas SelectionItem.Select does what the planner meant.
    if element.supports(PATTERN_INVOKE) or element.supports(PATTERN_LEGACY_IACCESSIBLE):
        method, act = "invoke", lambda: ctx.backend.invoke(element)
    elif element.supports(PATTERN_SELECTION_ITEM):
        method, act = "select_item", lambda: ctx.backend.select_item(element)
    elif element.supports(PATTERN_TOGGLE):
        method, act = "toggle", lambda: ctx.backend.toggle(element)
    else:
        method, act = "expand", lambda: ctx.backend.expand(element, expand=True)

    # A pattern invoke is stronger evidence than a synthetic click, but it is
    # still not proof the application finished responding — so it runs through
    # the same guards and the same completion accounting.
    completion = _guarded_input(ctx, act, context=f"{method} on {element.describe()}",
                                window=window)

    return OperationOutcome(
        stdout=(f"{method} -> {element.describe()}"
                + ("" if completion["completion_verified"] else " (completion unverified)")),
        evidence={"element": redact_element_payload(
                      element.to_dict(include_children=False)),
                  "interaction_method": method,
                  "resolution": resolution.to_dict(),
                  **completion},
        window_handle=window.handle if window else None,
    )


def _op_toggle_control(ctx: OperationContext) -> OperationOutcome:
    element, root, window, resolution = _find_element(
        ctx, require_patterns=(PATTERN_TOGGLE,))
    completion = _guarded_input(ctx, lambda: ctx.backend.toggle(element),
                                context=f"toggle {element.describe()}",
                                window=window)
    after = ctx.backend.refresh(element)
    return OperationOutcome(
        stdout=f"toggled {element.describe()} -> value={after.value!r}",
        evidence={"element_before": redact_element_payload(
                      element.to_dict(include_children=False)),
                  "element_after": redact_element_payload(
                      after.to_dict(include_children=False)),
                  "resolution": resolution.to_dict(),
                  **completion},
        window_handle=window.handle if window else None,
    )


def _op_expand_control(ctx: OperationContext) -> OperationOutcome:
    element, root, window, resolution = _find_element(
        ctx, require_patterns=(PATTERN_EXPAND_COLLAPSE,))
    expand = bool(ctx.arg("expand", True))
    completion = _guarded_input(
        ctx, lambda: ctx.backend.expand(element, expand=expand),
        context=f"{'expand' if expand else 'collapse'} {element.describe()}",
        window=window)
    return OperationOutcome(
        stdout=f"{'expanded' if expand else 'collapsed'} {element.describe()}",
        evidence={"element": redact_element_payload(
                      element.to_dict(include_children=False)),
                  "expand": expand, "resolution": resolution.to_dict(),
                  **completion},
        window_handle=window.handle if window else None,
    )


def _op_select_item(ctx: OperationContext) -> OperationOutcome:
    element, root, window, resolution = _find_element(
        ctx, require_patterns=(PATTERN_SELECTION_ITEM,))
    completion = _guarded_input(ctx, lambda: ctx.backend.select_item(element),
                                context=f"select {element.describe()}",
                                window=window)
    return OperationOutcome(
        stdout=f"selected {element.describe()}",
        evidence={"element": redact_element_payload(
                      element.to_dict(include_children=False)),
                  "resolution": resolution.to_dict(), **completion},
        window_handle=window.handle if window else None,
    )


def _op_set_text(ctx: OperationContext) -> OperationOutcome:
    text = ctx.require("text")
    if not isinstance(text, str):
        raise InvalidArguments("text must be a string",
                              details={"received_type": type(text).__name__})
    element, root, window, resolution = _find_element(
        ctx, require_patterns=(PATTERN_VALUE,))

    verify = bool(ctx.arg("verify", True))
    try:
        ctx.backend.set_value(element, text)
    except Exception as exc:
        # SetValue can fail having written part of the value. Mark it so a
        # non-idempotent caller is not told to blindly repeat.
        setattr(exc, "side_effect_possible", True)
        raise
    after = ctx.backend.refresh(element)

    if verify and (after.value or "") != text:
        # The brief's "must fail if contents are wrong": a set that silently
        # didn't take is a failure, not a success. Values are redacted here —
        # this payload lands in mission logs, and the text may be a credential.
        raise VerificationFailed(
            "control value did not match the requested text after set_value",
            details={
                "expected": redact_text(text),
                "actual": redact_text(after.value),
                "element": redact_element_payload(
                    after.to_dict(include_children=False)),
            },
            side_effect_possible=True,
        )

    return OperationOutcome(
        stdout=f"set text on {element.describe()} ({len(text)} chars)",
        evidence={"element_before": redact_element_payload(
                      element.to_dict(include_children=False)),
                  "element_after": redact_element_payload(
                      after.to_dict(include_children=False)),
                  "resolution": resolution.to_dict(),
                  # ValuePattern + read-back *is* a completion check, unlike
                  # synthesised input: the end state was observed directly.
                  "input_dispatched": True,
                  "completion_verified": bool(verify),
                  "verified": verify},
        window_handle=window.handle if window else None,
    )


def _op_type_text(ctx: OperationContext) -> OperationOutcome:
    text = ctx.require("text")
    if not isinstance(text, str):
        raise InvalidArguments("text must be a string",
                              details={"received_type": type(text).__name__})

    focused_element: ElementSnapshot | None = None
    resolution = None
    window: WindowInfo | None = None
    # Focusing a named target first is what makes typing deterministic; without
    # it the keystrokes go wherever focus happens to be.
    if ctx.arg("selector") or ctx.arg("name") or ctx.arg("automation_id"):
        focused_element, _root, window, resolution = _find_element(ctx)
        ctx.backend.focus_element(focused_element)
    else:
        window = _resolve_window(ctx, required=False)

    completion = _guarded_input(ctx, lambda: ctx.backend.type_text(text),
                                context=f"typing {len(text)} character(s)",
                                window=window)

    evidence: dict[str, Any] = {"typed_characters": len(text), **completion}
    if resolution is not None:
        evidence["resolution"] = resolution.to_dict()
    if focused_element is not None:
        evidence["target_element"] = redact_element_payload(
            focused_element.to_dict(include_children=False))
        after = ctx.backend.refresh(focused_element)
        evidence["element_after"] = redact_element_payload(
            after.to_dict(include_children=False))
    return OperationOutcome(
        stdout=(f"typed {len(text)} character(s)"
                + ("" if completion["completion_verified"] else " (completion unverified)")),
        evidence=evidence,
        window_handle=window.handle if window else None,
    )


def _op_send_keys(ctx: OperationContext) -> OperationOutcome:
    chords = parse_keys(ctx.require("keys"))
    window: WindowInfo | None = None
    target: ElementSnapshot | None = None
    resolution = None

    if ctx.arg("selector") or ctx.arg("name") or ctx.arg("automation_id"):
        target, _root, window, resolution = _find_element(ctx)
        ctx.backend.focus_element(target)
    else:
        window = _resolve_window(ctx, required=False)

    completion = _guarded_input(ctx, lambda: ctx.backend.send_keys(chords),
                                context=f"sending {describe_keys(chords)}",
                                window=window)

    evidence: dict[str, Any] = {"keys": [c.to_dict() for c in chords],
                                "keys_description": describe_keys(chords),
                                **completion}
    if resolution is not None:
        evidence["resolution"] = resolution.to_dict()
    if target is not None:
        evidence["target_element"] = redact_element_payload(
            target.to_dict(include_children=False))
    return OperationOutcome(
        stdout=(f"sent {describe_keys(chords)}"
                + ("" if completion["completion_verified"] else " (completion unverified)")),
        evidence=evidence,
        window_handle=window.handle if window else None,
    )


def _op_click_control(ctx: OperationContext) -> OperationOutcome:
    """Coordinate click at a *semantically located* element (goal 10).

    This is the fallback for controls with no usable pattern: the element is
    still found by meaning, and only the final press uses pixels. No
    hard-coded coordinates are involved.
    """
    element, root, window, resolution = _find_element(ctx)
    button = str(ctx.arg("button", "left")).lower()
    if button not in {"left", "right", "middle"}:
        raise InvalidArguments(f"unsupported mouse button {button!r}",
                               details={"button": button,
                                        "supported": ["left", "right", "middle"]})
    double = bool(ctx.arg("double", False))

    # Geometry is re-read here, not reused from discovery. Between resolving a
    # control and deciding to click it the window can move, resize, or change
    # monitor — and on a mixed-DPI multi-monitor desktop the same control's
    # physical coordinates differ per display. Remembered coordinates are how
    # a fallback clicks the wrong thing.
    rect = _fresh_rect(ctx, element)
    x, y = rect.center

    completion = _guarded_input(
        ctx, lambda: ctx.backend.click_point(x, y, button=button, double=double),
        context=f"{button} click at ({x},{y}) on {element.describe()}",
        window=window)

    return OperationOutcome(
        stdout=(f"{'double-' if double else ''}{button} click at "
                f"({x},{y}) on {element.describe()}"
                + ("" if completion["completion_verified"] else " (completion unverified)")),
        evidence={"element": redact_element_payload(
                      element.to_dict(include_children=False)),
                  "resolution": resolution.to_dict(),
                  "point": {"x": x, "y": y}, "button": button, "double": double,
                  "fallback_used": "coordinate_click",
                  **completion},
        window_handle=window.handle if window else None,
    )


def _op_click_point(ctx: OperationContext) -> OperationOutcome:
    """Raw coordinate click. Last resort; recorded as such in evidence."""
    try:
        x = int(ctx.require("x"))
        y = int(ctx.require("y"))
    except (TypeError, ValueError) as exc:
        raise InvalidArguments("x and y must be integers",
                               details={"x": ctx.arg("x"), "y": ctx.arg("y")}) from exc
    button = str(ctx.arg("button", "left")).lower()
    if button not in {"left", "right", "middle"}:
        raise InvalidArguments(f"unsupported mouse button {button!r}",
                               details={"button": button,
                                        "supported": ["left", "right", "middle"]})
    double = bool(ctx.arg("double", False))
    window = _resolve_window(ctx, required=False)

    completion = _guarded_input(
        ctx, lambda: ctx.backend.click_point(x, y, button=button, double=double),
        context=f"raw {button} click at ({x},{y})", window=window)

    return OperationOutcome(
        stdout=(f"{'double-' if double else ''}{button} click at ({x},{y})"
                + ("" if completion["completion_verified"] else " (completion unverified)")),
        evidence={"point": {"x": x, "y": y}, "button": button, "double": double,
                  "fallback_used": "raw_coordinate_click",
                  "warning": "raw coordinates are display-dependent and not "
                             "portable across resolutions, DPI settings, or "
                             "monitor arrangements; no element geometry backs "
                             "this click",
                  **completion},
        window_handle=window.handle if window else None,
    )


def _op_screenshot(ctx: OperationContext) -> OperationOutcome:
    from .evidence import capture_screenshot

    window = _resolve_window(ctx, required=False)
    label = str(ctx.arg("label", f"{ctx.action.id}-manual"))
    path, error = capture_screenshot(
        ctx.backend, label=label,
        window_handle=window.handle if window else None,
    )
    if path is None:
        raise UnsupportedUi(
            "screenshot capture unavailable",
            details={"error": error},
        )
    from .redaction import screenshot_record

    return OperationOutcome(
        stdout=f"screenshot -> {path}",
        evidence={"screenshot": screenshot_record(path, label=label)},
        screenshots=[path],
        window_handle=window.handle if window else None,
    )


def _op_close_window(ctx: OperationContext) -> OperationOutcome:
    """Close a window via its accessible Close affordance or WM_CLOSE.

    Deliberately *not* a process kill: killing a process loses unsaved work
    and is the sort of destructive shortcut this lane should never take.
    """
    window = _resolve_window(ctx, required=True)
    assert window is not None
    root = ctx.backend.control_tree(window_handle=window.handle, max_depth=4)
    keys = ctx.arg("keys", "alt+f4")

    # Prefer a real Close button if one is exposed.
    try:
        # Scoped to this window's own subtree: a desktop-wide "Close" search
        # would happily find another application's close button.
        close_button = resolve_one(
            root, Selector(name="Close", role="button", name_match="iequals"),
            require_unique=False)
    except ElementNotFound:
        close_button = None

    if close_button is not None and close_button.supports(PATTERN_INVOKE):
        ctx.backend.invoke(close_button)
        method = "invoke_close_button"
    else:
        ctx.backend.focus_window(window.handle)
        ctx.backend.send_keys(parse_keys(keys))
        method = f"send_keys({keys})"

    ctx.backend.sleep(float(ctx.arg("settle_seconds", 0.3)))
    remaining = [w for w in ctx.backend.list_windows(visible_only=False)
                 if w.handle == window.handle]
    return OperationOutcome(
        stdout=f"close requested via {method}; "
               f"window {'still present' if remaining else 'gone'}",
        evidence={"window": window.to_dict(), "method": method,
                  "window_still_present": bool(remaining)},
        window_handle=None if not remaining else window.handle,
    )


# ==========================================================================
# Registration table
# ==========================================================================

_MINIMAL = CapturePolicy.minimal
_STANDARD = CapturePolicy.standard


def _register_all() -> None:
    register(OperationSpec(
        name="capabilities", handler=_op_capabilities, read_only=True,
        description="Report backend capabilities and the supported operation set.",
        before=CapturePolicy(foreground=False), after=CapturePolicy(foreground=False),
    ))
    register(OperationSpec(
        name="list_windows", handler=_op_list_windows, read_only=True,
        description="Enumerate top-level windows (goal 1).",
        requires=("window_management",),
        before=CapturePolicy(foreground=False), after=CapturePolicy(foreground=False),
    ))
    register(OperationSpec(
        name="get_foreground_window", handler=_op_get_foreground_window, read_only=True,
        description="Identify the focused window (goal 2).",
        requires=("window_management",),
        before=CapturePolicy(foreground=False), after=CapturePolicy(foreground=False),
    ))
    register(OperationSpec(
        name="launch_application", handler=_op_launch_application,
        description="Start an application (goal 3).",
        requires=("process_launch",),
        # Launching twice starts a second instance.
        idempotent=False,
        before=_STANDARD(), after=_STANDARD(),
    ))
    register(OperationSpec(
        name="focus_window", handler=_op_focus_window,
        description="Bring an application window to the foreground (goal 4).",
        requires=("window_management",),
        before=_STANDARD(), after=_STANDARD(),
    ))
    register(OperationSpec(
        name="get_control_tree", handler=_op_get_control_tree, read_only=True,
        description="Inspect a window's UI Automation control tree (goal 5).",
        requires=("ui_automation",),
        before=CapturePolicy(foreground=False), after=CapturePolicy(foreground=False),
    ))
    register(OperationSpec(
        name="find_controls", handler=_op_find_controls, read_only=True,
        description="Find controls by name / role / automation id (goal 6).",
        requires=("ui_automation",),
        before=CapturePolicy(foreground=False), after=CapturePolicy(foreground=False),
    ))
    register(OperationSpec(
        name="get_element_state", handler=_op_get_element_state, read_only=True,
        description="Read one element's live properties.",
        requires=("ui_automation",),
        before=CapturePolicy(foreground=False), after=CapturePolicy(foreground=False),
    ))
    register(OperationSpec(
        name="wait_for_element", handler=_op_wait_for_element, read_only=True,
        description="Block until a selector resolves or the timeout expires.",
        requires=("ui_automation",),
        before=CapturePolicy(foreground=False), after=CapturePolicy(foreground=False),
    ))
    register(OperationSpec(
        name="invoke_control", handler=_op_invoke_control,
        description="Invoke a button or menu item (goal 7).",
        requires=("ui_automation",), before=_MINIMAL(), after=_MINIMAL(),
        # A second Invoke on Send, Save, or Delete does it again.
        idempotent=False, synthesises_input=True,
    ))
    register(OperationSpec(
        name="toggle_control", handler=_op_toggle_control,
        description="Flip a checkbox or toggle button.",
        requires=("ui_automation",), before=_MINIMAL(), after=_MINIMAL(),
        # Toggling twice returns to the original state — the opposite of a
        # no-op, and exactly why a blind retry is wrong.
        idempotent=False, synthesises_input=True,
    ))
    register(OperationSpec(
        name="expand_control", handler=_op_expand_control,
        description="Expand or collapse a menu, combo box, or tree item.",
        requires=("ui_automation",), before=_MINIMAL(), after=_MINIMAL(),
        # Expand(True) twice lands in the same state.
        idempotent=True, synthesises_input=True,
    ))
    register(OperationSpec(
        name="select_item", handler=_op_select_item,
        description="Select a list, tab, or tree item.",
        requires=("ui_automation",), before=_MINIMAL(), after=_MINIMAL(),
        idempotent=True, synthesises_input=True,
    ))
    register(OperationSpec(
        name="set_text", handler=_op_set_text,
        description="Set an edit control's text via ValuePattern (goal 8).",
        requires=("ui_automation",), before=_MINIMAL(), after=_MINIMAL(),
        # Setting the same value twice yields the same end state.
        idempotent=True,
    ))
    register(OperationSpec(
        name="type_text", handler=_op_type_text,
        description="Type literal text into the focused or selected control (goal 9).",
        requires=("keyboard",), before=_MINIMAL(), after=_MINIMAL(),
        # Typing appends: a retry duplicates the text.
        idempotent=False, synthesises_input=True,
    ))
    register(OperationSpec(
        name="send_keys", handler=_op_send_keys,
        description="Send keyboard chords such as ctrl+s (goal 9).",
        requires=("keyboard",), before=_MINIMAL(), after=_MINIMAL(),
        # Arbitrary chords have arbitrary effects; never assume repeatable.
        idempotent=False, synthesises_input=True,
    ))
    register(OperationSpec(
        name="click_control", handler=_op_click_control,
        description="Click a semantically located element's centre (goal 10).",
        requires=("mouse", "ui_automation"), before=_MINIMAL(), after=_MINIMAL(),
        idempotent=False, synthesises_input=True,
    ))
    register(OperationSpec(
        name="click_point", handler=_op_click_point,
        description="Raw coordinate click; last-resort fallback (goal 10).",
        requires=("mouse",), before=_MINIMAL(), after=_MINIMAL(),
        idempotent=False, synthesises_input=True,
    ))
    register(OperationSpec(
        name="screenshot", handler=_op_screenshot, read_only=True,
        description="Capture a screenshot as evidence (goal 11).",
        requires=("screenshots",),
        before=CapturePolicy(foreground=False), after=CapturePolicy(foreground=False),
    ))
    register(OperationSpec(
        name="close_window", handler=_op_close_window,
        description="Close a window via its Close affordance (never a process kill).",
        requires=("window_management",), before=_STANDARD(), after=_STANDARD(),
        # Closing an already-closed window is harmless, but a second alt+f4
        # lands on whatever window is behind it.
        idempotent=False, synthesises_input=True,
    ))


_register_all()


__all__ = [
    "REGISTRY", "OperationSpec", "OperationContext", "OperationOutcome",
    "Deadline", "get", "register",
]
