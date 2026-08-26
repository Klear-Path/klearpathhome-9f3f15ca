"""The Windows operator adapter.

One public entry point — :meth:`WindowsOperatorAdapter.execute` — taking a
Pilot Action and returning a Pilot Result. It owns no mission state, makes no
planning decisions, and never retries on its own: it reports ``retryable`` and
lets the mission controller decide.

The execute path is deliberately uniform:

1. Coerce the incoming Action.
2. Look up the operation; unknown verbs fail structurally.
3. Check the safety gate.
4. Check the backend actually supports what the operation needs.
5. Capture ``state_before``.
6. Run the handler under a cooperative deadline.
7. Capture ``state_after``.
8. Wrap everything — including any failure — into a Result.

Step 8 is the load-bearing one: no exception escapes ``execute``.
"""

from __future__ import annotations

import platform
import sys
import time
from typing import Any, Callable, Sequence

from .backend import BackendCapabilities, NullBackend
from .contracts import Action, Result, coerce_action
from .errors import (
    PlatformUnavailable,
    UnsupportedOperation,
    to_error_payload,
)
from .evidence import CapturePolicy, capture_screenshot, capture_state
from .operations import Deadline, OperationContext, OperationOutcome, REGISTRY, get
from . import safety


def default_backend() -> Any:
    """Pick the best backend available on this host.

    Returns a :class:`~.backend.NullBackend` rather than raising when Windows
    UIA is unavailable, so the adapter is constructible (and testable, and
    introspectable) on any platform. Actions then fail with a clear
    ``PLATFORM_UNAVAILABLE`` instead of an import traceback.
    """
    if sys.platform != "win32":
        return NullBackend(
            f"host platform is {sys.platform!r}, not 'win32'; "
            "the Windows operator adapter requires Windows"
        )
    try:
        from .uia_backend import UiaWindowsBackend

        return UiaWindowsBackend()
    except Exception as exc:  # missing comtypes, COM init failure, ...
        return NullBackend(f"Windows UIA backend unavailable: {type(exc).__name__}: {exc}")


class WindowsOperatorAdapter:
    """Executes Pilot Actions against a Windows desktop."""

    #: Identifier the core runtime routes on.
    tool = "windows_operator"

    def __init__(self, backend: Any | None = None, *,
                 allow_high_risk: bool = False,
                 capture_screenshots: bool = False,
                 clock: Callable[[], float] = time.monotonic) -> None:
        """
        ``allow_high_risk``
            Off by default. The core runtime turns it on only once it has
            operator authorisation for the mission.
        ``capture_screenshots``
            Off by default because screen capture is expensive and, on a real
            desktop, may capture unrelated windows. Missions that need visual
            evidence opt in.
        """
        self.backend = backend if backend is not None else default_backend()
        self.allow_high_risk = allow_high_risk
        self.capture_screenshots = capture_screenshots
        self._clock = clock

    # --- introspection --------------------------------------------------

    def capabilities(self) -> BackendCapabilities:
        return self.backend.capabilities()

    def supported_operations(self) -> dict[str, str]:
        return {name: spec.description for name, spec in sorted(REGISTRY.items())}

    def available(self) -> bool:
        """Whether this adapter can actually drive a desktop right now."""
        caps = self.capabilities()
        return bool(caps.ui_automation or caps.vision)

    def describe(self) -> dict[str, Any]:
        """Everything the core runtime needs to register this adapter."""
        caps = self.capabilities()
        return {
            "tool": self.tool,
            "available": self.available(),
            "host": {
                "platform": sys.platform,
                "release": platform.release(),
                "python": sys.version.split()[0],
            },
            "capabilities": caps.to_dict(),
            "operations": self.supported_operations(),
            "allow_high_risk": self.allow_high_risk,
        }

    # --- execution ------------------------------------------------------

    def execute(self, action: Any) -> Result:
        """Execute one Action. Never raises."""
        started = self._clock()
        try:
            coerced = coerce_action(action)
        except Exception as exc:
            # A malformed Action has no usable id, so report against whatever
            # the caller gave us rather than inventing one.
            return Result(
                action_id=str(getattr(action, "id", None)
                              or (action.get("id") if isinstance(action, dict) else "")
                              or "unknown"),
                success=False,
                error=to_error_payload(exc),
                retryable=False,
                duration_seconds=round(self._clock() - started, 4),
            )

        result = Result(action_id=coerced.id, success=False)
        state_before: dict[str, Any] = {}
        screenshots: list[str] = []

        try:
            spec = get(coerced.operation)

            safety_decision = safety.check(coerced, allow_high_risk=self.allow_high_risk)
            self._assert_backend_supports(spec)

            deadline = Deadline(coerced.timeout_seconds, now=self._clock)
            ctx = OperationContext(action=coerced, backend=self.backend, deadline=deadline)

            state_before = capture_state(
                self.backend, spec.before, label="before",
            )
            if self.capture_screenshots and spec.before.screenshot:
                path, err = capture_screenshot(self.backend, label=f"{coerced.id}-before")
                if path:
                    screenshots.append(path)
                elif err:
                    state_before.setdefault("capture_errors", []).append(err)

            outcome: OperationOutcome = spec.handler(ctx)

            state_after = capture_state(
                self.backend, spec.after, label="after",
                window_handle=outcome.window_handle,
            )
            if self.capture_screenshots and spec.after.screenshot:
                path, err = capture_screenshot(
                    self.backend, label=f"{coerced.id}-after",
                    window_handle=outcome.window_handle,
                )
                if path:
                    screenshots.append(path)
                elif err:
                    state_after.setdefault("capture_errors", []).append(err)
            screenshots.extend(outcome.screenshots)

            result.success = True
            result.state_before = state_before
            result.state_after = state_after
            result.stdout = outcome.stdout
            result.screenshots = screenshots
            result.evidence = {
                "operation": coerced.operation,
                "tool": self.tool,
                "safety": safety_decision,
                "backend": self.capabilities().to_dict(),
                **outcome.evidence,
            }
            result.duration_seconds = round(self._clock() - started, 4)
            return result

        except Exception as exc:
            # Every failure — classified OperatorError or unexpected fault —
            # becomes a Result. The mission controller must always get an
            # answer, so nothing escapes this method.
            return self._failure(coerced, exc, started, state_before, screenshots)

    def execute_all(self, actions: Sequence[Any], *,
                    stop_on_failure: bool = True) -> list[Result]:
        """Run a sequence of Actions in order.

        A convenience for scripted proofs, *not* a mission controller: there is
        no planning, no branching, and no retry. ``stop_on_failure`` exists so
        a proof does not push keystrokes into an application that failed to
        launch.
        """
        results: list[Result] = []
        for action in actions:
            outcome = self.execute(action)
            results.append(outcome)
            if stop_on_failure and not outcome.success:
                break
        return results

    # --- internals ------------------------------------------------------

    def _assert_backend_supports(self, spec: Any) -> None:
        caps = self.capabilities()
        missing = [need for need in spec.requires if not getattr(caps, need, False)]
        if missing:
            # Distinguish "this host cannot do desktop automation at all" from
            # "this backend lacks one specific facility": they call for
            # completely different responses from the planner.
            if not (caps.ui_automation or caps.vision):
                raise PlatformUnavailable(
                    f"backend {caps.name!r} cannot drive a desktop "
                    f"({caps.notes or 'no UI automation available'})",
                    details={"capabilities": caps.to_dict(),
                             "missing": missing,
                             "operation": spec.name},
                )
            raise UnsupportedOperation(
                f"backend {caps.name!r} does not support {missing} "
                f"required by operation {spec.name!r}",
                details={"capabilities": caps.to_dict(),
                         "missing": missing, "operation": spec.name},
            )

    def _failure(self, action: Action, exc: BaseException, started: float,
                 state_before: dict[str, Any],
                 screenshots: list[str]) -> Result:
        payload = to_error_payload(exc)
        state_after: dict[str, Any] = {}
        try:
            # Post-failure state is often the most valuable evidence there is
            # (which dialog actually appeared), so try for it — but never let
            # capture failure mask the original error.
            state_after = capture_state(self.backend, CapturePolicy.minimal(),
                                        label="after_failure")
        except Exception:
            state_after = {"label": "after_failure", "capture_errors": ["unavailable"]}

        return Result(
            action_id=action.id,
            success=False,
            state_before=state_before,
            state_after=state_after,
            evidence={
                "operation": action.operation,
                "tool": self.tool,
                "arguments": dict(action.arguments),
            },
            stderr=payload["message"],
            screenshots=screenshots,
            error=payload,
            retryable=bool(payload.get("retryable", False)),
            duration_seconds=round(self._clock() - started, 4),
        )


__all__ = ["WindowsOperatorAdapter", "default_backend"]
