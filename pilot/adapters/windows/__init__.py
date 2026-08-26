"""KlearFlow Pilot — Windows operator adapter.

Native Windows computer-control lane. Exposes one adapter that turns Pilot
Actions into desktop work via UI Automation, with deterministic keyboard/mouse
as the second choice and coordinate interaction as an explicit fallback.

Importing this package is safe on any platform: the backend degrades to
:class:`~.backend.NullBackend` off Windows rather than failing at import.
"""

from __future__ import annotations

from .adapter import WindowsOperatorAdapter, default_backend
from .backend import BackendCapabilities, NullBackend, UiaBackend
from .contracts import Action, Result, RiskLevel, TOOL_NAME, coerce_action
from .errors import OperatorError, to_error_payload
from .keyboard import Chord, parse_chord, parse_keys
from .model import ElementSnapshot, Rect, WindowInfo
from .operations import REGISTRY
from .control_selectors import Selector

__all__ = [
    "WindowsOperatorAdapter",
    "default_backend",
    "Action",
    "Result",
    "RiskLevel",
    "TOOL_NAME",
    "coerce_action",
    "Selector",
    "ElementSnapshot",
    "WindowInfo",
    "Rect",
    "Chord",
    "parse_chord",
    "parse_keys",
    "UiaBackend",
    "BackendCapabilities",
    "NullBackend",
    "OperatorError",
    "to_error_payload",
    "REGISTRY",
]

__version__ = "0.1.0"
