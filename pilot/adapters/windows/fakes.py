"""Deterministic in-memory backend and simulated stock applications.

Two jobs:

1. Give the unit suite a backend it can drive precisely — including failure
   modes that are hard to provoke on a real desktop (a disabled control, a
   pattern-less custom surface, a window that refuses focus).
2. Let the proof missions in :mod:`.missions` execute end-to-end on any
   platform, against simulated Notepad and Calculator.

**What this does and does not prove.** The simulated applications reproduce the
*control structure and interaction contract* of their real counterparts —
automation ids, control types, accessible patterns, the Save-As dialog flow —
so a mission run here genuinely exercises selector resolution, ordering,
verification, and error handling. It does **not** exercise UIA, COM, or
``SendInput``. Only the Windows integration suite does that. The fake Notepad
does perform real filesystem writes, so the on-disk verification step is not
simulated.

Time is virtual: :meth:`FakeBackend.sleep` advances an internal clock, so
timeout and polling behaviour is testable without wall-clock delay.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

from .backend import BackendCapabilities
from .errors import (
    ElementNotFound,
    ElementNotInteractable,
    LaunchFailed,
    UnsupportedUi,
    WindowNotFound,
)
from .keyboard import Chord, describe_keys
from .model import (
    PATTERN_EXPAND_COLLAPSE,
    PATTERN_INVOKE,
    PATTERN_SELECTION_ITEM,
    PATTERN_TEXT,
    PATTERN_TOGGLE,
    PATTERN_VALUE,
    PATTERN_WINDOW,
    ElementSnapshot,
    Rect,
    WindowInfo,
)


@dataclass
class FakeElement:
    """A mutable simulated UI element."""

    runtime_id: str
    name: str = ""
    role: str = ""
    automation_id: str = ""
    class_name: str = ""
    value: str | None = None
    enabled: bool = True
    offscreen: bool = False
    keyboard_focusable: bool = False
    rect: Rect = field(default_factory=lambda: Rect(0, 0, 100, 30))
    patterns: tuple[str, ...] = ()
    children: list["FakeElement"] = field(default_factory=list)
    read_only: bool = False
    #: Called when the element is invoked/selected/toggled. Receives the owning
    #: :class:`FakeApp` so handlers can mutate application state.
    on_invoke: Callable[["FakeApp", "FakeElement"], None] | None = None
    #: Called when set_value succeeds, after the value is stored.
    on_value_set: Callable[["FakeApp", "FakeElement", str], None] | None = None

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    def find(self, runtime_id: str) -> "FakeElement | None":
        for node in self.walk():
            if node.runtime_id == runtime_id:
                return node
        return None


@dataclass
class FakeApp:
    """A simulated top-level window plus its behaviour."""

    handle: int
    title: str
    process_id: int
    process_name: str
    root: FakeElement
    class_name: str = "FakeWindowClass"
    rect: Rect = field(default_factory=lambda: Rect(0, 0, 1024, 768))
    is_visible: bool = True
    is_minimized: bool = False
    #: Refuse foreground focus, simulating Windows' foreground lock.
    refuses_focus: bool = False
    #: Simulated modality. Drives the unexpected-modal guard.
    is_modal: bool = False
    #: Simulated Windows integrity level of the owning process.
    integrity_level: str = "medium"
    #: Chord description (e.g. "ctrl+s") -> handler.
    key_handlers: dict[str, Callable[["FakeApp", "FakeBackend"], None]] = field(default_factory=dict)
    #: Free-form application state the handlers use.
    state: dict[str, Any] = field(default_factory=dict)
    #: Runtime id of the element holding keyboard focus.
    focused_runtime_id: str | None = None

    def element(self, runtime_id: str) -> FakeElement:
        found = self.root.find(runtime_id)
        if found is None:
            raise ElementNotFound(f"no element {runtime_id} in {self.title!r}",
                                  details={"runtime_id": runtime_id})
        return found

    def to_window_info(self, *, foreground: bool) -> WindowInfo:
        return WindowInfo(
            handle=self.handle, title=self.title, process_id=self.process_id,
            process_name=self.process_name, class_name=self.class_name,
            rect=self.rect, is_foreground=foreground,
            is_minimized=self.is_minimized, is_visible=self.is_visible,
            is_modal=self.is_modal, integrity_level=self.integrity_level,
        )


class FakeBackend:
    """In-memory :class:`~.backend.UiaBackend` implementation."""

    def __init__(self, *, apps: Sequence[FakeApp] = (),
                 launchers: dict[str, Callable[["FakeBackend"], FakeApp]] | None = None,
                 supports_screenshots: bool = True,
                 screenshot_dir: str | None = None) -> None:
        self.apps: list[FakeApp] = list(apps)
        self.launchers = dict(launchers or {})
        self.foreground_handle: int | None = self.apps[0].handle if self.apps else None
        self.supports_screenshots = supports_screenshots
        self.screenshot_dir = screenshot_dir
        self._next_handle = max((a.handle for a in self.apps), default=1000) + 1
        self._next_pid = 5000
        #: Ordered log of every backend call, for assertions about *how* an
        #: operation was performed (pattern vs. keystroke vs. coordinates).
        self.calls: list[tuple[str, Any]] = []
        self.typed: list[str] = []
        self.keys_sent: list[str] = []
        self.clicks: list[tuple[int, int, str, bool]] = []
        self.slept: float = 0.0
        self._now = 1000.0
        self.launch_failures: dict[str, Exception] = {}
        #: Simulated integrity level of this (the operator) process.
        self.own_integrity = "medium"
        #: Reports the backend can read integrity levels at all.
        self.supports_integrity = True
        #: When set, ``element_rect`` offsets the returned rect by (dx, dy).
        #: Simulates a window moving between discovery and click — the
        #: multi-monitor / DPI-change case.
        self.geometry_drift: tuple[int, int] = (0, 0)
        #: When set, ``element_rect`` raises this instead of answering.
        self.geometry_error: Exception | None = None

    # --- clock ----------------------------------------------------------

    def clock(self) -> float:
        """Virtual monotonic clock. Pass to the adapter as ``clock=``."""
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds

    def sleep(self, seconds: float) -> None:
        if seconds > 0:
            self.slept += seconds
            self._now += seconds

    # --- helpers --------------------------------------------------------

    def add_app(self, app: FakeApp, *, focus: bool = True) -> FakeApp:
        self.apps.append(app)
        if focus:
            self.foreground_handle = app.handle
        return app

    def remove_app(self, handle: int) -> None:
        self.apps = [a for a in self.apps if a.handle != handle]
        if self.foreground_handle == handle:
            self.foreground_handle = self.apps[-1].handle if self.apps else None

    def app(self, handle: int) -> FakeApp:
        for candidate in self.apps:
            if candidate.handle == handle:
                return candidate
        raise WindowNotFound(f"no window {handle}", details={"handle": handle})

    def foreground_app(self) -> FakeApp | None:
        if self.foreground_handle is None:
            return None
        try:
            return self.app(self.foreground_handle)
        except WindowNotFound:
            return None

    def allocate_handle(self) -> int:
        self._next_handle += 1
        return self._next_handle

    def allocate_pid(self) -> int:
        self._next_pid += 1
        return self._next_pid

    def _owner_of(self, runtime_id: str) -> FakeApp:
        for app in self.apps:
            if app.root.find(runtime_id) is not None:
                return app
        raise ElementNotFound(f"element {runtime_id} not found in any window",
                              details={"runtime_id": runtime_id})

    # --- capabilities ---------------------------------------------------

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            name="fake", platform="fake",
            ui_automation=True, keyboard=True, mouse=True,
            screenshots=self.supports_screenshots,
            process_launch=True, window_management=True,
            integrity_levels=self.supports_integrity,
            notes="deterministic in-memory backend for tests and mission dry-runs",
        )

    # --- integrity & geometry -------------------------------------------

    def current_integrity(self) -> str:
        self.calls.append(("current_integrity", None))
        return self.own_integrity

    def process_integrity(self, process_id: int) -> str:
        self.calls.append(("process_integrity", process_id))
        for app in self.apps:
            if app.process_id == process_id:
                return app.integrity_level
        return ""

    def element_rect(self, element: ElementSnapshot) -> Rect:
        """Current geometry, honouring any injected drift."""
        self.calls.append(("element_rect", element.runtime_id))
        if self.geometry_error is not None:
            raise self.geometry_error
        app = self._owner_of(element.runtime_id)
        node = app.element(element.runtime_id)
        dx, dy = self.geometry_drift
        return Rect(left=node.rect.left + dx, top=node.rect.top + dy,
                    right=node.rect.right + dx, bottom=node.rect.bottom + dy)

    # --- windows --------------------------------------------------------

    def list_windows(self, *, visible_only: bool = True) -> list[WindowInfo]:
        self.calls.append(("list_windows", visible_only))
        return [
            app.to_window_info(foreground=app.handle == self.foreground_handle)
            for app in self.apps
            if not visible_only or app.is_visible
        ]

    def foreground_window(self) -> WindowInfo | None:
        self.calls.append(("foreground_window", None))
        app = self.foreground_app()
        return app.to_window_info(foreground=True) if app else None

    def focus_window(self, handle: int) -> WindowInfo:
        self.calls.append(("focus_window", handle))
        app = self.app(handle)
        if app.refuses_focus:
            # Report the *actual* state rather than raising: the operation layer
            # is responsible for noticing focus did not move.
            return app.to_window_info(foreground=self.foreground_handle == handle)
        app.is_minimized = False
        self.foreground_handle = handle
        return app.to_window_info(foreground=True)

    # --- process --------------------------------------------------------

    def launch(self, command: str, *, arguments: Sequence[str] = (),
               working_directory: str | None = None,
               wait_for_window_seconds: float = 10.0) -> tuple[int, WindowInfo | None]:
        self.calls.append(("launch", (command, tuple(arguments))))
        stem = os.path.splitext(os.path.basename(command))[0].casefold()
        if stem in self.launch_failures:
            raise self.launch_failures[stem]
        factory = self.launchers.get(stem)
        if factory is None:
            raise LaunchFailed(f"fake backend has no launcher for {command!r}",
                               details={"command": command,
                                        "known": sorted(self.launchers)})
        app = factory(self)
        self.add_app(app, focus=True)
        return app.process_id, app.to_window_info(foreground=True)

    # --- control tree ---------------------------------------------------

    def _snapshot(self, app: FakeApp, node: FakeElement, depth: int,
                  max_depth: int, budget: dict[str, int]) -> ElementSnapshot:
        budget["remaining"] -= 1
        children: tuple[ElementSnapshot, ...] = ()
        if depth < max_depth and budget["remaining"] > 0:
            built = []
            for child in node.children:
                if budget["remaining"] <= 0:
                    break
                built.append(self._snapshot(app, child, depth + 1, max_depth, budget))
            children = tuple(built)
        return ElementSnapshot(
            runtime_id=node.runtime_id, name=node.name, role=node.role,
            automation_id=node.automation_id, class_name=node.class_name,
            value=node.value, enabled=node.enabled, offscreen=node.offscreen,
            focused=app.focused_runtime_id == node.runtime_id,
            keyboard_focusable=node.keyboard_focusable, rect=node.rect,
            patterns=tuple(node.patterns), depth=depth, children=children,
            process_id=app.process_id, window_handle=app.handle,
        )

    def control_tree(self, *, window_handle: int | None = None,
                     max_depth: int = 12,
                     max_elements: int = 2000) -> ElementSnapshot:
        self.calls.append(("control_tree", window_handle))
        if window_handle is None:
            app = self.foreground_app()
            if app is None:
                raise WindowNotFound("no foreground window to inspect", details={})
        else:
            app = self.app(int(window_handle))
        return self._snapshot(app, app.root, 0, max_depth,
                              {"remaining": max(1, max_elements)})

    def refresh(self, element: ElementSnapshot) -> ElementSnapshot:
        self.calls.append(("refresh", element.runtime_id))
        app = self._owner_of(element.runtime_id)
        node = app.element(element.runtime_id)
        return self._snapshot(app, node, element.depth, element.depth,
                              {"remaining": 1})

    # --- interaction ----------------------------------------------------

    def _require_pattern(self, element: ElementSnapshot, node: FakeElement,
                         pattern: str, label: str) -> None:
        if pattern not in node.patterns:
            raise UnsupportedUi(
                f"element does not support {label}: {element.describe()}",
                details={"element": element.to_dict(include_children=False),
                         "advertised_patterns": list(node.patterns)},
            )

    def invoke(self, element: ElementSnapshot) -> None:
        self.calls.append(("invoke", element.runtime_id))
        app = self._owner_of(element.runtime_id)
        node = app.element(element.runtime_id)
        self._require_pattern(element, node, PATTERN_INVOKE, "Invoke")
        if not node.enabled:
            raise ElementNotInteractable(f"disabled: {element.describe()}",
                                         details={"runtime_id": element.runtime_id})
        if node.on_invoke:
            node.on_invoke(app, node)

    def set_value(self, element: ElementSnapshot, value: str) -> None:
        self.calls.append(("set_value", (element.runtime_id, value)))
        app = self._owner_of(element.runtime_id)
        node = app.element(element.runtime_id)
        self._require_pattern(element, node, PATTERN_VALUE, "Value")
        if node.read_only:
            raise ElementNotInteractable(f"read-only: {element.describe()}",
                                         details={"runtime_id": element.runtime_id})
        node.value = value
        if node.on_value_set:
            node.on_value_set(app, node, value)

    def focus_element(self, element: ElementSnapshot) -> None:
        self.calls.append(("focus_element", element.runtime_id))
        app = self._owner_of(element.runtime_id)
        node = app.element(element.runtime_id)
        if not node.keyboard_focusable:
            raise ElementNotInteractable(
                f"not keyboard focusable: {element.describe()}",
                details={"runtime_id": element.runtime_id})
        app.focused_runtime_id = node.runtime_id
        self.foreground_handle = app.handle

    def toggle(self, element: ElementSnapshot) -> None:
        self.calls.append(("toggle", element.runtime_id))
        app = self._owner_of(element.runtime_id)
        node = app.element(element.runtime_id)
        self._require_pattern(element, node, PATTERN_TOGGLE, "Toggle")
        node.value = "off" if node.value == "on" else "on"
        if node.on_invoke:
            node.on_invoke(app, node)

    def select_item(self, element: ElementSnapshot) -> None:
        self.calls.append(("select_item", element.runtime_id))
        app = self._owner_of(element.runtime_id)
        node = app.element(element.runtime_id)
        self._require_pattern(element, node, PATTERN_SELECTION_ITEM, "SelectionItem")
        if node.on_invoke:
            node.on_invoke(app, node)

    def expand(self, element: ElementSnapshot, *, expand: bool = True) -> None:
        self.calls.append(("expand", (element.runtime_id, expand)))
        app = self._owner_of(element.runtime_id)
        node = app.element(element.runtime_id)
        self._require_pattern(element, node, PATTERN_EXPAND_COLLAPSE, "ExpandCollapse")
        node.value = "expanded" if expand else "collapsed"

    # --- keyboard & mouse -----------------------------------------------

    def send_keys(self, chords: Sequence[Chord]) -> None:
        description = describe_keys(chords)
        self.calls.append(("send_keys", description))
        self.keys_sent.append(description)
        app = self.foreground_app()
        if app is None:
            return
        for chord in chords:
            handler = app.key_handlers.get(chord.describe())
            if handler:
                handler(app, self)
                # The handler may have swapped the foreground window (opened a
                # dialog); subsequent chords go to whatever is in front now.
                app = self.foreground_app()
                if app is None:
                    return

    def type_text(self, text: str) -> None:
        self.calls.append(("type_text", text))
        self.typed.append(text)
        app = self.foreground_app()
        if app is None or app.focused_runtime_id is None:
            return
        node = app.root.find(app.focused_runtime_id)
        if node is None or PATTERN_VALUE not in node.patterns or node.read_only:
            return
        node.value = (node.value or "") + text

    def click_point(self, x: int, y: int, *, button: str = "left",
                    double: bool = False) -> None:
        self.calls.append(("click_point", (x, y, button, double)))
        self.clicks.append((x, y, button, double))
        # Hit-test so a coordinate click still drives the simulated app: this is
        # what lets the fallback path be tested for effect, not just for having
        # been called. Real hit-testing resolves to the *topmost* element, so
        # the deepest containing node wins — otherwise every click would land
        # on the window root, whose rect contains everything.
        def _deepest_hit(node: FakeElement, depth: int) -> tuple[int, FakeElement] | None:
            rect = node.rect
            if not (rect.left <= x < rect.right and rect.top <= y < rect.bottom):
                return None
            best: tuple[int, FakeElement] | None = (depth, node) if node.enabled else None
            for child in node.children:
                hit = _deepest_hit(child, depth + 1)
                if hit is not None and (best is None or hit[0] >= best[0]):
                    best = hit
            return best

        for app in reversed(self.apps):
            if not app.is_visible:
                continue
            hit = _deepest_hit(app.root, 0)
            if hit is not None:
                node = hit[1]
                if node.on_invoke:
                    node.on_invoke(app, node)
                return

    # --- evidence -------------------------------------------------------

    def screenshot(self, *, window_handle: int | None = None,
                   path: str | None = None) -> str | None:
        self.calls.append(("screenshot", window_handle))
        if not self.supports_screenshots:
            return None
        target = path or os.path.join(self.screenshot_dir or ".", "fake.png")
        os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
        # A real 1x1 PNG so downstream consumers can open the artefact.
        with open(target, "wb") as handle:
            handle.write(
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
                b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00"
                b"\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
            )
        return target


# ==========================================================================
# Simulated stock applications
# ==========================================================================

def _notepad_save_as_dialog(notepad: FakeApp, backend: FakeBackend) -> FakeApp:
    """Build the Save As dialog, mirroring the real control contract.

    Real Notepad's Save As is a common item dialog: a "File name:" combo/edit
    (automation id ``1001`` on the classic dialog) and a "Save" button. Those
    are the handles a mission targets, so the simulation exposes the same ones.
    """
    filename_edit = FakeElement(
        runtime_id="saveas.filename", name="File name:", role="edit",
        automation_id="1001", class_name="Edit", value="",
        keyboard_focusable=True, patterns=(PATTERN_VALUE, PATTERN_TEXT),
        rect=Rect(200, 400, 600, 424),
    )
    save_button = FakeElement(
        runtime_id="saveas.save", name="Save", role="button",
        automation_id="1", class_name="Button", keyboard_focusable=True,
        patterns=(PATTERN_INVOKE,), rect=Rect(610, 400, 690, 424),
    )
    cancel_button = FakeElement(
        runtime_id="saveas.cancel", name="Cancel", role="button",
        automation_id="2", class_name="Button", keyboard_focusable=True,
        patterns=(PATTERN_INVOKE,), rect=Rect(700, 400, 780, 424),
    )
    dialog_root = FakeElement(
        runtime_id="saveas.root", name="Save As", role="window",
        class_name="#32770", patterns=(PATTERN_WINDOW,),
        rect=Rect(150, 200, 850, 500),
        children=[filename_edit, save_button, cancel_button],
    )
    dialog = FakeApp(
        handle=backend.allocate_handle(), title="Save As",
        process_id=notepad.process_id, process_name=notepad.process_name,
        root=dialog_root, class_name="#32770", rect=Rect(150, 200, 850, 500),
        state={"owner_handle": notepad.handle},
        is_modal=True,
    )

    def _do_save(app: FakeApp, _node: FakeElement) -> None:
        raw_path = (filename_edit.value or "").strip()
        if not raw_path:
            # The real dialog simply refuses and stays open.
            return
        owner = backend.app(app.state["owner_handle"])
        editor = owner.root.find("notepad.editor")
        content = (editor.value if editor else "") or ""
        directory = os.path.dirname(os.path.abspath(raw_path))
        if directory:
            os.makedirs(directory, exist_ok=True)
        # Real Notepad writes UTF-8 with CRLF line endings by default on
        # current Windows builds; matching that keeps the on-disk assertion
        # meaningful rather than accidentally lenient.
        with open(raw_path, "w", encoding="utf-8", newline="\r\n") as handle:
            handle.write(content)
        owner.state["saved_path"] = raw_path
        owner.title = f"{os.path.basename(raw_path)} - Notepad"
        backend.remove_app(app.handle)
        backend.foreground_handle = owner.handle

    def _do_cancel(app: FakeApp, _node: FakeElement) -> None:
        backend.remove_app(app.handle)
        backend.foreground_handle = app.state["owner_handle"]

    save_button.on_invoke = _do_save
    cancel_button.on_invoke = _do_cancel
    return dialog


def make_fake_notepad(backend: FakeBackend) -> FakeApp:
    """Simulated Notepad.

    Control contract mirrors the real application: a single Document-role
    editor (class ``Edit``/``RichEditD2DPT`` depending on build, automation id
    ``15``) supporting Value and Text patterns, plus a File menu. ``ctrl+s``
    opens Save As the first time and saves in place afterwards.
    """
    editor = FakeElement(
        runtime_id="notepad.editor", name="Text editor", role="document",
        automation_id="15", class_name="Edit", value="",
        keyboard_focusable=True, patterns=(PATTERN_VALUE, PATTERN_TEXT),
        rect=Rect(0, 60, 1024, 700),
    )
    file_menu = FakeElement(
        runtime_id="notepad.menu.file", name="File", role="menu_item",
        class_name="MenuItem", keyboard_focusable=True,
        patterns=(PATTERN_INVOKE, PATTERN_EXPAND_COLLAPSE),
        rect=Rect(8, 30, 48, 54),
    )
    menu_bar = FakeElement(
        runtime_id="notepad.menubar", name="Application", role="menu_bar",
        class_name="MenuBar", rect=Rect(0, 30, 1024, 54), children=[file_menu],
    )
    root = FakeElement(
        runtime_id="notepad.root", name="Untitled - Notepad", role="window",
        class_name="Notepad", patterns=(PATTERN_WINDOW,),
        rect=Rect(0, 0, 1024, 768), children=[menu_bar, editor],
    )
    app = FakeApp(
        handle=backend.allocate_handle(), title="Untitled - Notepad",
        process_id=backend.allocate_pid(), process_name="notepad.exe",
        root=root, class_name="Notepad", rect=Rect(0, 0, 1024, 768),
        focused_runtime_id="notepad.editor",
    )

    def _on_save(owner: FakeApp, be: FakeBackend) -> None:
        existing = owner.state.get("saved_path")
        if existing:
            with open(existing, "w", encoding="utf-8", newline="\r\n") as handle:
                handle.write(editor.value or "")
            return
        be.add_app(_notepad_save_as_dialog(owner, be), focus=True)

    def _on_close(owner: FakeApp, be: FakeBackend) -> None:
        be.remove_app(owner.handle)

    app.key_handlers["ctrl+s"] = _on_save
    app.key_handlers["alt+f4"] = _on_close
    return app


def make_fake_calculator(backend: FakeBackend) -> FakeApp:
    """Simulated Calculator.

    Mirrors the real app's automation ids (``num7Button``, ``plusButton``,
    ``equalButton``, ``CalculatorResults``) and the "Display is N" accessible
    name pattern, because those are precisely what a coordinate-free mission
    has to rely on.
    """
    display = FakeElement(
        runtime_id="calc.display", name="Display is 0", role="text",
        automation_id="CalculatorResults", class_name="TextBlock",
        value="0", patterns=(PATTERN_TEXT,), rect=Rect(20, 80, 380, 140),
    )

    def _update_display(app: FakeApp) -> None:
        display.value = str(app.state["display"])
        display.name = f"Display is {app.state['display']}"

    def _digit(digit: int):
        def _handler(app: FakeApp, _node: FakeElement) -> None:
            if app.state.get("fresh", True):
                app.state["display"] = str(digit)
                app.state["fresh"] = False
            else:
                app.state["display"] = f"{app.state['display']}{digit}"
            _update_display(app)
        return _handler

    def _plus(app: FakeApp, _node: FakeElement) -> None:
        app.state["accumulator"] = int(app.state["display"])
        app.state["pending"] = "+"
        app.state["fresh"] = True

    def _equals(app: FakeApp, _node: FakeElement) -> None:
        if app.state.get("pending") == "+":
            total = app.state.get("accumulator", 0) + int(app.state["display"])
            app.state["display"] = str(total)
            app.state["pending"] = None
            app.state["fresh"] = True
            _update_display(app)

    def _clear(app: FakeApp, _node: FakeElement) -> None:
        app.state.update({"display": "0", "accumulator": 0,
                          "pending": None, "fresh": True})
        _update_display(app)

    names = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
             6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 0: "Zero"}
    buttons: list[FakeElement] = []
    for index, digit in enumerate(sorted(names)):
        column, row = index % 3, index // 3
        buttons.append(FakeElement(
            runtime_id=f"calc.num{digit}", name=names[digit], role="button",
            automation_id=f"num{digit}Button", class_name="Button",
            keyboard_focusable=True, patterns=(PATTERN_INVOKE,),
            rect=Rect(20 + column * 90, 200 + row * 60,
                      100 + column * 90, 255 + row * 60),
            on_invoke=_digit(digit),
        ))
    buttons.append(FakeElement(
        runtime_id="calc.plus", name="Plus", role="button",
        automation_id="plusButton", class_name="Button", keyboard_focusable=True,
        patterns=(PATTERN_INVOKE,), rect=Rect(290, 200, 370, 255), on_invoke=_plus,
    ))
    buttons.append(FakeElement(
        runtime_id="calc.equals", name="Equals", role="button",
        automation_id="equalButton", class_name="Button", keyboard_focusable=True,
        patterns=(PATTERN_INVOKE,), rect=Rect(290, 260, 370, 315), on_invoke=_equals,
    ))
    buttons.append(FakeElement(
        runtime_id="calc.clear", name="Clear", role="button",
        automation_id="clearButton", class_name="Button", keyboard_focusable=True,
        patterns=(PATTERN_INVOKE,), rect=Rect(290, 320, 370, 375), on_invoke=_clear,
    ))
    # A deliberately inaccessible surface: exercises goal-13 detection.
    buttons.append(FakeElement(
        runtime_id="calc.custom_surface", name="", role="custom",
        automation_id="", class_name="DirectUIHWND",
        rect=Rect(400, 200, 500, 300), patterns=(),
    ))

    root = FakeElement(
        runtime_id="calc.root", name="Calculator", role="window",
        class_name="ApplicationFrameWindow", patterns=(PATTERN_WINDOW,),
        rect=Rect(0, 0, 420, 600), children=[display, *buttons],
    )
    app = FakeApp(
        handle=backend.allocate_handle(), title="Calculator",
        process_id=backend.allocate_pid(),
        process_name="ApplicationFrameHost.exe", root=root,
        class_name="ApplicationFrameWindow", rect=Rect(0, 0, 420, 600),
        state={"display": "0", "accumulator": 0, "pending": None, "fresh": True},
    )
    return app


def make_uac_prompt(backend: FakeBackend) -> FakeApp:
    """A simulated UAC consent prompt on the secure desktop."""
    return FakeApp(
        handle=backend.allocate_handle(), title="User Account Control",
        process_id=backend.allocate_pid(), process_name="consent.exe",
        class_name="Credential Dialog Xaml Host",
        root=FakeElement(runtime_id="uac.root", name="User Account Control",
                         role="window", children=[
                             FakeElement(runtime_id="uac.yes", name="Yes",
                                         role="button", patterns=(PATTERN_INVOKE,)),
                         ]),
        is_modal=True, integrity_level="system",
    )


def make_elevated_app(backend: FakeBackend, *, title: str = "Elevated Tool") -> FakeApp:
    """A simulated application running at high integrity."""
    return FakeApp(
        handle=backend.allocate_handle(), title=title,
        process_id=backend.allocate_pid(), process_name="admin_tool.exe",
        root=FakeElement(runtime_id="elev.root", name=title, role="window",
                         children=[
                             FakeElement(runtime_id="elev.ok", name="OK",
                                         role="button", patterns=(PATTERN_INVOKE,),
                                         keyboard_focusable=True),
                         ]),
        integrity_level="high",
    )


def make_unexpected_dialog(backend: FakeBackend, owner: FakeApp, *,
                           title: str = "Confirm Save As") -> FakeApp:
    """The overwrite-confirmation nobody planned for."""
    return FakeApp(
        handle=backend.allocate_handle(), title=title,
        process_id=owner.process_id, process_name=owner.process_name,
        class_name="#32770",
        root=FakeElement(runtime_id="confirm.root", name=title, role="window",
                         children=[
                             FakeElement(runtime_id="confirm.yes", name="Yes",
                                         role="button", patterns=(PATTERN_INVOKE,)),
                             FakeElement(runtime_id="confirm.no", name="No",
                                         role="button", patterns=(PATTERN_INVOKE,)),
                         ]),
        is_modal=True,
    )


def make_desktop() -> FakeBackend:
    """A backend that can launch the simulated stock applications."""
    return FakeBackend(launchers={
        "notepad": make_fake_notepad,
        "calc": make_fake_calculator,
        "calculator": make_fake_calculator,
    })


__all__ = [
    "FakeBackend", "FakeApp", "FakeElement",
    "make_fake_notepad", "make_fake_calculator", "make_desktop",
    "make_uac_prompt", "make_elevated_app", "make_unexpected_dialog",
]
