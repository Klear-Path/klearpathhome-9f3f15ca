"""The backend seam.

:class:`UiaBackend` is the *only* interface through which this lane touches a
desktop. Everything above it (selectors, operations, adapter, missions) is
platform-free, so the entire lane is exercised on any OS by substituting a
fake backend.

That seam is also where the planned vision fallback plugs in: a
vision-assisted backend implements the same protocol, and
:class:`BackendCapabilities` lets the adapter report what a given backend can
actually do rather than discovering it by exception. See README.md
("Adding a vision fallback").

Execution preference, per the lane brief, is encoded in the method set: the
UIA-level operations come first, deterministic keyboard/mouse next, and
coordinate clicking is a named fallback (:meth:`click_point`) rather than the
primary path.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Protocol, Sequence, runtime_checkable

from .keyboard import Chord
from .model import ElementSnapshot, WindowInfo


@dataclass(frozen=True)
class BackendCapabilities:
    """What a backend can do, declared up front.

    The adapter consults this before dispatching, so an operation a backend
    genuinely cannot perform yields ``UNSUPPORTED_OPERATION`` with a clear
    reason instead of a confusing crash deep in a driver.
    """

    name: str
    platform: str
    ui_automation: bool = False
    keyboard: bool = False
    mouse: bool = False
    screenshots: bool = False
    process_launch: bool = False
    window_management: bool = False
    #: Set by a future vision backend; recorded in evidence so the mission log
    #: shows whether a step used accessibility or pixels.
    vision: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@runtime_checkable
class UiaBackend(Protocol):
    """Operations a Windows-control backend must provide."""

    # --- introspection --------------------------------------------------

    def capabilities(self) -> BackendCapabilities:
        """Describe what this backend supports. Must not raise."""
        ...

    # --- windows (goals 1, 2, 4) ----------------------------------------

    def list_windows(self, *, visible_only: bool = True) -> list[WindowInfo]:
        """All top-level windows."""
        ...

    def foreground_window(self) -> WindowInfo | None:
        """The window with input focus, or ``None`` if nothing has focus."""
        ...

    def focus_window(self, handle: int) -> WindowInfo:
        """Bring a window to the foreground and return its refreshed state."""
        ...

    # --- process (goal 3) -----------------------------------------------

    def launch(self, command: str, *, arguments: Sequence[str] = (),
               working_directory: str | None = None,
               wait_for_window_seconds: float = 10.0) -> tuple[int, WindowInfo | None]:
        """Start a program.

        Returns ``(process_id, first_window)``. ``first_window`` is ``None``
        when the process started but produced no top-level window inside
        ``wait_for_window_seconds`` — a real and distinguishable outcome
        (console tools, splash-screen-only startup), not an error.
        """
        ...

    # --- control tree (goals 5, 6) --------------------------------------

    def control_tree(self, *, window_handle: int | None = None,
                     max_depth: int = 12,
                     max_elements: int = 2000) -> ElementSnapshot:
        """Snapshot a window's UIA subtree.

        Bounded on purpose: unbounded UIA walks on a complex application can
        take minutes and allocate enormous trees. Callers get the truncation
        counters back through the returned tree's stats.
        """
        ...

    def refresh(self, element: ElementSnapshot) -> ElementSnapshot:
        """Re-read one element's live properties (no children required)."""
        ...

    # --- interaction (goals 7, 8) ---------------------------------------

    def invoke(self, element: ElementSnapshot) -> None:
        """Press a button / activate a menu item via the accessible pattern."""
        ...

    def set_value(self, element: ElementSnapshot, value: str) -> None:
        """Set a control's text via the ValuePattern (no keystroke simulation)."""
        ...

    def focus_element(self, element: ElementSnapshot) -> None:
        """Give an element keyboard focus."""
        ...

    def toggle(self, element: ElementSnapshot) -> None:
        """Flip a checkbox / toggle button via its accessible pattern."""
        ...

    def select_item(self, element: ElementSnapshot) -> None:
        """Select a list/tab/tree item via its accessible pattern."""
        ...

    def expand(self, element: ElementSnapshot, *, expand: bool = True) -> None:
        """Expand or collapse a menu / combo / tree item."""
        ...

    # --- keyboard & mouse (goals 9, 10) ---------------------------------

    def send_keys(self, chords: Sequence[Chord]) -> None:
        """Send parsed chords to whatever currently has focus."""
        ...

    def type_text(self, text: str) -> None:
        """Type literal text, Unicode included, without chord interpretation."""
        ...

    def click_point(self, x: int, y: int, *, button: str = "left",
                    double: bool = False) -> None:
        """Coordinate click. The explicit last-resort path."""
        ...

    # --- evidence (goal 11) ---------------------------------------------

    def screenshot(self, *, window_handle: int | None = None,
                   path: str | None = None) -> str | None:
        """Capture a PNG and return its path, or ``None`` if unsupported."""
        ...

    def sleep(self, seconds: float) -> None:
        """Settle-wait hook. Injected so tests need no wall-clock delay."""
        ...


class NullBackend:
    """A backend that supports nothing.

    Used when the host is not Windows or the UIA stack is unavailable, so the
    adapter can be constructed anywhere and answer capability questions
    truthfully instead of failing at import time. Every action it is handed
    fails with ``PLATFORM_UNAVAILABLE``.
    """

    def __init__(self, reason: str) -> None:
        self.reason = reason

    def capabilities(self) -> BackendCapabilities:
        import sys

        return BackendCapabilities(
            name="null",
            platform=sys.platform,
            notes=self.reason,
        )

    def _fail(self, *_args: Any, **_kwargs: Any):
        from .errors import PlatformUnavailable

        raise PlatformUnavailable(
            f"Windows operator backend unavailable: {self.reason}",
            details={"reason": self.reason},
        )

    # Every protocol method funnels to the same refusal.
    list_windows = foreground_window = focus_window = _fail
    launch = control_tree = refresh = _fail
    invoke = set_value = focus_element = toggle = select_item = expand = _fail
    send_keys = type_text = click_point = _fail
    screenshot = _fail

    def sleep(self, seconds: float) -> None:  # harmless, keeps the protocol whole
        return None


__all__ = ["UiaBackend", "BackendCapabilities", "NullBackend"]
