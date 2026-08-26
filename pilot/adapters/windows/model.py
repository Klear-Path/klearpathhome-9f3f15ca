"""Platform-free value objects describing observed UI state.

Nothing here imports Windows APIs. The real UIA backend converts live COM
objects into these snapshots; the fake backend in the unit suite constructs
them directly. Every module above this one (selectors, operations, adapter,
missions) sees only these types, which is what lets the whole lane be tested
off-Windows.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Iterator


@dataclass(frozen=True)
class Rect:
    """A screen rectangle in physical pixels."""

    left: int = 0
    top: int = 0
    right: int = 0
    bottom: int = 0

    @property
    def width(self) -> int:
        return max(0, self.right - self.left)

    @property
    def height(self) -> int:
        return max(0, self.bottom - self.top)

    @property
    def is_empty(self) -> bool:
        return self.width <= 0 or self.height <= 0

    @property
    def center(self) -> tuple[int, int]:
        return (self.left + self.width // 2, self.top + self.height // 2)

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


#: UIA ControlType localised names we normalise to. Keys are the loose spellings
#: a planner might emit; values are the canonical role string. Matching is done
#: on the canonical form so "Button"/"button"/"ButtonControl" all agree.
_ROLE_ALIASES = {
    "button": "button",
    "buttoncontrol": "button",
    "push button": "button",
    "edit": "edit",
    "editcontrol": "edit",
    "textbox": "edit",
    "text box": "edit",
    "text": "text",
    "textcontrol": "text",
    "label": "text",
    "static": "text",
    "document": "document",
    "documentcontrol": "document",
    "menuitem": "menu_item",
    "menu item": "menu_item",
    "menu_item": "menu_item",
    "menu": "menu",
    "menubar": "menu_bar",
    "menu bar": "menu_bar",
    "menu_bar": "menu_bar",
    "window": "window",
    "windowcontrol": "window",
    "dialog": "window",
    "pane": "pane",
    "panecontrol": "pane",
    "group": "group",
    "checkbox": "check_box",
    "check box": "check_box",
    "check_box": "check_box",
    "radiobutton": "radio_button",
    "radio button": "radio_button",
    "radio_button": "radio_button",
    "combobox": "combo_box",
    "combo box": "combo_box",
    "combo_box": "combo_box",
    "list": "list",
    "listitem": "list_item",
    "list item": "list_item",
    "list_item": "list_item",
    "tab": "tab",
    "tabitem": "tab_item",
    "tab item": "tab_item",
    "tree": "tree",
    "treeitem": "tree_item",
    "toolbar": "tool_bar",
    "tool bar": "tool_bar",
    "tool_bar": "tool_bar",
    "hyperlink": "hyperlink",
    "link": "hyperlink",
    "image": "image",
    "custom": "custom",
    "spinner": "spinner",
    "slider": "slider",
    "statusbar": "status_bar",
    "status bar": "status_bar",
    "titlebar": "title_bar",
    "title bar": "title_bar",
}


def normalize_role(role: str | None) -> str:
    """Fold a role/control-type spelling to this lane's canonical form.

    Unknown roles pass through lowercased rather than being rejected: UIA
    providers invent control types, and refusing to represent one would make
    the tree less useful than describing it imperfectly.
    """
    if not role:
        return ""
    key = str(role).strip().lower()
    if key in _ROLE_ALIASES:
        return _ROLE_ALIASES[key]
    # Strip the "…Control" / "ControlType." decorations UIA bindings add.
    if key.startswith("controltype."):
        key = key[len("controltype."):]
    if key.endswith("control") and len(key) > len("control"):
        stripped = key[: -len("control")]
        if stripped in _ROLE_ALIASES:
            return _ROLE_ALIASES[stripped]
        key = stripped
    return _ROLE_ALIASES.get(key, key)


#: Accessible interaction patterns the adapter cares about. The backend reports
#: which of these an element advertises; operations check the list before
#: attempting an interaction, which is how "unsupported UI" is detected up
#: front instead of by exception.
PATTERN_INVOKE = "invoke"
PATTERN_VALUE = "value"
PATTERN_TEXT = "text"
PATTERN_TOGGLE = "toggle"
PATTERN_EXPAND_COLLAPSE = "expand_collapse"
PATTERN_SELECTION_ITEM = "selection_item"
PATTERN_WINDOW = "window"
PATTERN_LEGACY_IACCESSIBLE = "legacy_iaccessible"


@dataclass(frozen=True)
class ElementSnapshot:
    """An immutable observation of one UI element.

    ``runtime_id`` is the backend's handle back to the live element. It is
    opaque to every layer above the backend; treat it as a cookie.
    """

    runtime_id: str
    name: str = ""
    role: str = ""
    automation_id: str = ""
    class_name: str = ""
    value: str | None = None
    enabled: bool = True
    offscreen: bool = False
    focused: bool = False
    keyboard_focusable: bool = False
    rect: Rect = field(default_factory=Rect)
    patterns: tuple[str, ...] = ()
    depth: int = 0
    children: tuple["ElementSnapshot", ...] = ()
    process_id: int = 0
    window_handle: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "role", normalize_role(self.role))

    @property
    def interactable(self) -> bool:
        """Whether a deterministic interaction is plausible right now."""
        return self.enabled and not self.offscreen

    def supports(self, pattern: str) -> bool:
        return pattern in self.patterns

    def walk(self) -> Iterator["ElementSnapshot"]:
        """Depth-first traversal including ``self``."""
        yield self
        for child in self.children:
            yield from child.walk()

    def to_dict(self, *, include_children: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "runtime_id": self.runtime_id,
            "name": self.name,
            "role": self.role,
            "automation_id": self.automation_id,
            "class_name": self.class_name,
            "value": self.value,
            "enabled": self.enabled,
            "offscreen": self.offscreen,
            "focused": self.focused,
            "keyboard_focusable": self.keyboard_focusable,
            "rect": self.rect.to_dict(),
            "patterns": list(self.patterns),
            "depth": self.depth,
            "process_id": self.process_id,
            "window_handle": self.window_handle,
        }
        if include_children:
            payload["children"] = [c.to_dict() for c in self.children]
        return payload

    def describe(self) -> str:
        """One-line human-readable label, used in evidence and error messages."""
        bits = [self.role or "element"]
        if self.name:
            bits.append(f'name={self.name!r}')
        if self.automation_id:
            bits.append(f"automation_id={self.automation_id!r}")
        if not self.enabled:
            bits.append("disabled")
        if self.offscreen:
            bits.append("offscreen")
        return " ".join(bits)


#: Window classes Windows uses for dialogs. ``#32770`` is the classic dialog
#: class; the others are the modern XAML / task-dialog hosts.
DIALOG_CLASS_NAMES = frozenset({
    "#32770",
    "taskdialog",
    "credential dialog xaml host",
    "xamlexplorerhostislandwindow",
})

#: Processes that host UAC consent UI. Interacting with these is refused
#: outright — see :class:`~.errors.UacPromptDetected`.
UAC_PROCESS_NAMES = frozenset({
    "consent.exe",
    "credentialuibroker.exe",
})

#: Windows integrity levels, lowest to highest. Comparing by index is what
#: makes an elevation *mismatch* detectable rather than merely observable.
INTEGRITY_ORDER = ("untrusted", "low", "medium", "medium_plus", "high", "system")


def integrity_rank(level: str | None) -> int:
    """Numeric rank of an integrity level, or -1 when unknown.

    Unknown ranks -1 so an unreadable target never compares as *higher* than
    this process and trip a spurious elevation error; callers test for -1
    explicitly when "could not determine" is itself significant.
    """
    if not level:
        return -1
    try:
        return INTEGRITY_ORDER.index(str(level).strip().lower())
    except ValueError:
        return -1


@dataclass(frozen=True)
class WindowInfo:
    """A top-level window."""

    handle: int
    title: str = ""
    process_id: int = 0
    process_name: str = ""
    class_name: str = ""
    rect: Rect = field(default_factory=Rect)
    is_foreground: bool = False
    is_minimized: bool = False
    is_visible: bool = True
    #: True when the window is modal or dialog-shaped. Drives the
    #: unexpected-modal guard.
    is_modal: bool = False
    #: Windows integrity level of the owning process, or "" when unreadable.
    integrity_level: str = ""

    @property
    def is_dialog_class(self) -> bool:
        return (self.class_name or "").strip().lower() in DIALOG_CLASS_NAMES

    @property
    def is_uac_prompt(self) -> bool:
        return (self.process_name or "").strip().lower() in UAC_PROCESS_NAMES

    @property
    def identity(self) -> tuple[int, int, str]:
        """Handle + process identity, for before/after comparison.

        The process half is what matters for focus-theft detection: an
        application legitimately moving focus between its own windows is a
        different event from another process stealing it.
        """
        return (self.handle, self.process_id, self.process_name or "")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["rect"] = self.rect.to_dict()
        payload["is_dialog_class"] = self.is_dialog_class
        return payload


def flatten(root: ElementSnapshot, *, max_depth: int | None = None) -> list[ElementSnapshot]:
    """Flatten a snapshot tree, optionally pruning below ``max_depth``."""
    out: list[ElementSnapshot] = []
    stack: list[ElementSnapshot] = [root]
    while stack:
        node = stack.pop()
        if max_depth is not None and node.depth > max_depth:
            continue
        out.append(node)
        stack.extend(reversed(node.children))
    return out


def summarize_tree(root: ElementSnapshot, *, limit: int = 40) -> list[dict[str, Any]]:
    """Compact, evidence-sized listing of a control tree.

    Deliberately lossy: full trees for a real application run to thousands of
    nodes and would swamp a Result payload. ``limit`` caps it, and the caller
    is told how many were dropped via :func:`describe_tree_stats`.
    """
    rows: list[dict[str, Any]] = []
    for node in flatten(root):
        if len(rows) >= limit:
            break
        rows.append({
            "runtime_id": node.runtime_id,
            "depth": node.depth,
            "role": node.role,
            "name": node.name,
            "automation_id": node.automation_id,
            "enabled": node.enabled,
            "patterns": list(node.patterns),
        })
    return rows


def describe_tree_stats(root: ElementSnapshot) -> dict[str, Any]:
    """Aggregate counts for a control tree, cheap enough to always attach."""
    nodes = flatten(root)
    by_role: dict[str, int] = {}
    interactable = 0
    named = 0
    for node in nodes:
        by_role[node.role or "unknown"] = by_role.get(node.role or "unknown", 0) + 1
        if node.interactable and node.patterns:
            interactable += 1
        if node.name:
            named += 1
    return {
        "total_elements": len(nodes),
        "named_elements": named,
        "interactable_elements": interactable,
        "max_depth": max((n.depth for n in nodes), default=0),
        "roles": dict(sorted(by_role.items(), key=lambda kv: (-kv[1], kv[0]))),
    }


__all__ = [
    "Rect",
    "ElementSnapshot",
    "WindowInfo",
    "DIALOG_CLASS_NAMES",
    "UAC_PROCESS_NAMES",
    "INTEGRITY_ORDER",
    "integrity_rank",
    "normalize_role",
    "flatten",
    "summarize_tree",
    "describe_tree_stats",
    "PATTERN_INVOKE",
    "PATTERN_VALUE",
    "PATTERN_TEXT",
    "PATTERN_TOGGLE",
    "PATTERN_EXPAND_COLLAPSE",
    "PATTERN_SELECTION_ITEM",
    "PATTERN_WINDOW",
    "PATTERN_LEGACY_IACCESSIBLE",
]
