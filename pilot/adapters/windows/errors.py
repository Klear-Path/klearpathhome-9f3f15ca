"""Structured failure taxonomy for the Windows operator lane.

Goal 12 of the lane brief is "return structured failures instead of
crashing". Every error below carries three things the mission controller needs
in order to decide what to do next without parsing prose:

``code``
    A stable machine-readable string. Safe to branch on.
``retryable``
    Whether repeating the identical action could plausibly succeed. Transient
    UI states (element not yet present, window still opening) are retryable;
    contract violations and inaccessible UI are not.
``details``
    Operation-specific structured context (which selector missed, which
    patterns the element did support, and so on).
"""

from __future__ import annotations

from typing import Any


class OperatorError(Exception):
    """Base class for every failure this adapter names.

    Anything *not* derived from this is an unexpected fault; the adapter
    catches those too and reports them as ``INTERNAL_ERROR`` so the process
    never dies on the mission controller's behalf.
    """

    code = "OPERATOR_ERROR"
    retryable = False
    #: Whether the operation may already have changed the target's state before
    #: failing. This is *independent* of ``retryable``: an error can be
    #: transient and still leave a half-applied side effect. The adapter
    #: combines the two with the operation's idempotency to decide the
    #: ``retryable`` it actually reports (see ``adapter._resolve_retryable``).
    #: Defaulting to True would make every discovery failure unretryable, so it
    #: defaults False and handlers set it once input has been dispatched.
    side_effect_possible = False

    def __init__(self, message: str, *, details: dict[str, Any] | None = None,
                 retryable: bool | None = None,
                 side_effect_possible: bool | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}
        if retryable is not None:
            self.retryable = retryable
        if side_effect_possible is not None:
            self.side_effect_possible = side_effect_possible

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
            "side_effect_possible": self.side_effect_possible,
            "details": self.details,
        }


# --- Contract / programmer-facing failures (never retryable) ---------------

class UnsupportedOperation(OperatorError):
    """The requested operation is not implemented by this adapter."""

    code = "UNSUPPORTED_OPERATION"
    retryable = False


class InvalidArguments(OperatorError):
    """Arguments were missing, malformed, or mutually contradictory."""

    code = "INVALID_ARGUMENTS"
    retryable = False


class PlatformUnavailable(OperatorError):
    """This adapter cannot run here at all (non-Windows host, missing UIA)."""

    code = "PLATFORM_UNAVAILABLE"
    retryable = False


class SafetyRefusal(OperatorError):
    """A KlearForge safety gate declined the action.

    Raised, for example, when a high-risk irreversible action arrives without
    the confirmation token the gate requires. Never retryable by repetition:
    the *action* has to change, not the timing.
    """

    code = "SAFETY_REFUSAL"
    retryable = False


class ElevationRequired(OperatorError):
    """The target runs at a higher integrity level than this process.

    Windows' UIPI blocks input and much of UIA across an integrity boundary.
    Retrying cannot fix it and neither can this adapter: the operator must
    restart the Pilot process at a matching integrity level. Escalate to a
    human rather than attempting a workaround.
    """

    code = "ELEVATION_REQUIRED"
    retryable = False


class UacPromptDetected(OperatorError):
    """A UAC consent prompt is on screen.

    This adapter never drives consent UI — not to accept it, not to dismiss
    it. Approving an elevation request is a decision a human makes. Execution
    stops here.
    """

    code = "UAC_PROMPT_DETECTED"
    retryable = False


class UnexpectedModal(OperatorError):
    """A dialog appeared that the action did not declare.

    Continuing would push input at whatever is now in front, so execution
    stops. The planner either handles the dialog or re-issues the action
    declaring it via ``expect``/``allow_modals``.
    """

    code = "UNEXPECTED_MODAL"
    retryable = False


class ForegroundChanged(OperatorError):
    """Foreground focus moved to another process around an input event.

    The synthesised keystrokes or clicks may have landed in an unrelated
    application, so the action's outcome is unknown rather than merely failed.
    Never silently retryable: what the input did must be established first.
    """

    code = "FOREGROUND_CHANGED"
    retryable = False
    side_effect_possible = True


class CompletionUnverified(OperatorError):
    """Input was dispatched but the declared post-condition never held.

    Delivering a keystroke proves the keystroke was delivered and nothing
    more. This is the failure raised when ``expect`` was supplied and the
    expected end state did not appear.
    """

    code = "COMPLETION_UNVERIFIED"
    retryable = False
    side_effect_possible = True


class StaleElement(OperatorError):
    """The resolved element moved or changed between discovery and use.

    Acting on stale geometry is how coordinate fallbacks click the wrong
    thing. Retryable, because re-discovery is exactly the right response.
    """

    code = "STALE_ELEMENT"
    retryable = True


# --- Environment / target-state failures ----------------------------------

class WindowNotFound(OperatorError):
    """No top-level window matched the request."""

    code = "WINDOW_NOT_FOUND"
    retryable = True


class ElementNotFound(OperatorError):
    """No UI element matched the selector within the timeout."""

    code = "ELEMENT_NOT_FOUND"
    retryable = True


class AmbiguousSelector(OperatorError):
    """The selector matched more than one element and the caller demanded one.

    Not retryable: repeating the same ambiguous selector stays ambiguous. The
    details payload lists the candidates so the planner can narrow it.
    """

    code = "AMBIGUOUS_SELECTOR"
    retryable = False


class ElementNotInteractable(OperatorError):
    """The element was found but is disabled, offscreen, or hidden."""

    code = "ELEMENT_NOT_INTERACTABLE"
    retryable = True


class UnsupportedUi(OperatorError):
    """The element exposes no accessible pattern for the requested interaction.

    This is the goal-13 signal: obviously inaccessible UI (a bare rendering
    surface, a custom-drawn control with no UIA patterns). Not retryable via
    UIA — it is the hand-off point for the future vision fallback, which is
    why ``details`` records the patterns the element *did* advertise.
    """

    code = "UNSUPPORTED_UI"
    retryable = False


class LaunchFailed(OperatorError):
    """The application could not be started."""

    code = "LAUNCH_FAILED"
    retryable = True


class TimeoutExpired(OperatorError):
    """The action exceeded ``Action.timeout_seconds``."""

    code = "TIMEOUT"
    retryable = True


class BackendError(OperatorError):
    """The underlying automation stack raised an error we could not classify.

    Treated as retryable: COM calls against a UI tree that is mid-repaint fail
    transiently often enough that one retry is usually worth it.
    """

    code = "BACKEND_ERROR"
    retryable = True


class VerificationFailed(OperatorError):
    """The action ran but the observed end state did not match expectations.

    Distinct from a backend error on purpose: the mechanics worked, the
    *outcome* was wrong. Proof missions rely on this to fail loudly rather
    than reporting a hollow success.
    """

    code = "VERIFICATION_FAILED"
    retryable = False


def to_error_payload(exc: BaseException) -> dict[str, Any]:
    """Render any exception as a Result ``error`` payload."""
    if isinstance(exc, OperatorError):
        return exc.to_dict()
    return {
        "code": "INTERNAL_ERROR",
        "message": f"{type(exc).__name__}: {exc}",
        "retryable": False,
        # An unclassified fault gives no way to know how far the operation got,
        # so assume it may have acted. Fails safe for non-idempotent work.
        "side_effect_possible": True,
        "details": {"exception_type": type(exc).__name__},
    }


def is_retryable(exc: BaseException) -> bool:
    return bool(getattr(exc, "retryable", False))


def has_side_effect(exc: BaseException) -> bool:
    """Whether ``exc`` may have left the target changed.

    Unclassified exceptions are assumed to have acted: the operation could
    have failed anywhere, including after dispatching input.
    """
    if isinstance(exc, OperatorError):
        return bool(exc.side_effect_possible)
    return True


__all__ = [
    "OperatorError",
    "UnsupportedOperation",
    "InvalidArguments",
    "PlatformUnavailable",
    "SafetyRefusal",
    "ElevationRequired",
    "UacPromptDetected",
    "UnexpectedModal",
    "ForegroundChanged",
    "CompletionUnverified",
    "StaleElement",
    "WindowNotFound",
    "ElementNotFound",
    "AmbiguousSelector",
    "ElementNotInteractable",
    "UnsupportedUi",
    "LaunchFailed",
    "TimeoutExpired",
    "BackendError",
    "VerificationFailed",
    "to_error_payload",
    "is_retryable",
    "has_side_effect",
]
