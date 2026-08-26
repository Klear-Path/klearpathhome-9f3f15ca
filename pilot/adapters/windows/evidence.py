"""State capture before and after each action (lane goal 11).

Two design decisions worth stating:

1. Capture must never fail an action. If evidence collection throws, the
   failure is recorded *as* evidence and the action proceeds. A screenshot
   that cannot be taken is not a reason to abandon a save.
2. Capture is scoped by operation. Snapshotting a full control tree around
   every keystroke would dominate runtime, so operations declare how much
   state they need via :class:`CapturePolicy`.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from typing import Any

from .model import WindowInfo, describe_tree_stats, summarize_tree


@dataclass(frozen=True)
class CapturePolicy:
    """How much state to record around one operation."""

    foreground: bool = True
    window_list: bool = False
    control_tree: bool = False
    screenshot: bool = False
    tree_limit: int = 40

    #: Sensible presets.
    @staticmethod
    def minimal() -> "CapturePolicy":
        return CapturePolicy(foreground=True)

    @staticmethod
    def standard() -> "CapturePolicy":
        return CapturePolicy(foreground=True, window_list=True)

    @staticmethod
    def full() -> "CapturePolicy":
        return CapturePolicy(foreground=True, window_list=True,
                             control_tree=True, screenshot=True)


def _screenshot_dir() -> str:
    """Where screenshots land.

    Overridable via ``KLEARFLOW_PILOT_EVIDENCE_DIR`` so a mission run can keep
    its artefacts together; falls back to a temp subdirectory.
    """
    configured = os.environ.get("KLEARFLOW_PILOT_EVIDENCE_DIR")
    target = configured or os.path.join(tempfile.gettempdir(), "klearflow-pilot-evidence")
    os.makedirs(target, exist_ok=True)
    return target


def capture_state(backend: Any, policy: CapturePolicy, *,
                  label: str,
                  window_handle: int | None = None) -> dict[str, Any]:
    """Best-effort state snapshot.

    Returns a dict that always contains ``label`` and ``capture_errors``, so a
    consumer can tell "nothing was there" from "we could not look".
    """
    state: dict[str, Any] = {"label": label, "capture_errors": []}

    def _try(key: str, fn):
        try:
            state[key] = fn()
        except Exception as exc:  # evidence must never break the action
            state["capture_errors"].append({
                "field": key,
                "error": f"{type(exc).__name__}: {exc}",
            })

    if policy.foreground:
        def _fg():
            window = backend.foreground_window()
            return window.to_dict() if isinstance(window, WindowInfo) else None
        _try("foreground_window", _fg)

    if policy.window_list:
        def _windows():
            return [w.to_dict() for w in backend.list_windows()]
        _try("windows", _windows)

    if policy.control_tree:
        def _tree():
            root = backend.control_tree(window_handle=window_handle)
            return {
                "root": root.to_dict(include_children=False),
                "stats": describe_tree_stats(root),
                "elements": summarize_tree(root, limit=policy.tree_limit),
            }
        _try("control_tree", _tree)

    return state


def capture_screenshot(backend: Any, *, label: str,
                       window_handle: int | None = None) -> tuple[str | None, dict[str, Any] | None]:
    """Capture one screenshot. Returns ``(path, error)``; at most one is set."""
    try:
        caps = backend.capabilities()
        if not getattr(caps, "screenshots", False):
            return None, {"field": "screenshot", "error": "backend reports no screenshot support"}
        path = os.path.join(_screenshot_dir(), f"{label}.png")
        produced = backend.screenshot(window_handle=window_handle, path=path)
        return (produced, None) if produced else (None, {
            "field": "screenshot", "error": "backend returned no path"
        })
    except Exception as exc:
        return None, {"field": "screenshot", "error": f"{type(exc).__name__}: {exc}"}


__all__ = ["CapturePolicy", "capture_state", "capture_screenshot"]
