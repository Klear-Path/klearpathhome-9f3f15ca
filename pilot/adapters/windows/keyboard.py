"""Keyboard chord parsing (lane goal 9).

Turning ``"ctrl+shift+s"`` into a deterministic key sequence is exactly the
kind of logic that must not live inside a COM call: it is fiddly, it has edge
cases, and it needs to be verified without a desktop. The backend receives
already-validated :class:`Chord` objects and only has to press keys.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .errors import InvalidArguments

#: Canonical modifier names.
MOD_CTRL = "ctrl"
MOD_ALT = "alt"
MOD_SHIFT = "shift"
MOD_WIN = "win"

_MODIFIER_ALIASES = {
    "ctrl": MOD_CTRL, "control": MOD_CTRL, "ctl": MOD_CTRL, "^": MOD_CTRL,
    "alt": MOD_ALT, "menu": MOD_ALT, "%": MOD_ALT,
    "shift": MOD_SHIFT, "shft": MOD_SHIFT, "+": MOD_SHIFT,
    "win": MOD_WIN, "super": MOD_WIN, "meta": MOD_WIN, "cmd": MOD_WIN,
    "windows": MOD_WIN, "lwin": MOD_WIN,
}

#: Named non-printable keys the adapter accepts. Values are this lane's
#: canonical spelling; the backend maps them onto virtual key codes.
_NAMED_KEYS = {
    "enter": "enter", "return": "enter", "ret": "enter",
    "tab": "tab",
    "esc": "escape", "escape": "escape",
    "space": "space", "spacebar": "space",
    "backspace": "backspace", "bksp": "backspace", "bs": "backspace",
    "delete": "delete", "del": "delete",
    "insert": "insert", "ins": "insert",
    "home": "home", "end": "end",
    "pageup": "page_up", "page_up": "page_up", "pgup": "page_up",
    "pagedown": "page_down", "page_down": "page_down", "pgdn": "page_down",
    "up": "up", "down": "down", "left": "left", "right": "right",
    "uparrow": "up", "downarrow": "down", "leftarrow": "left", "rightarrow": "right",
    "printscreen": "print_screen", "print_screen": "print_screen",
    "capslock": "caps_lock", "caps_lock": "caps_lock",
    "numlock": "num_lock", "num_lock": "num_lock",
    "scrolllock": "scroll_lock", "scroll_lock": "scroll_lock",
    "pause": "pause", "break": "pause",
    "apps": "apps", "menukey": "apps", "contextmenu": "apps",
}
for _i in range(1, 25):
    _NAMED_KEYS[f"f{_i}"] = f"f{_i}"

#: Single printable characters are allowed as-is; anything else must be named.
_MAX_KEY_TOKEN = max(len(k) for k in _NAMED_KEYS)


@dataclass(frozen=True)
class Chord:
    """One keystroke: zero or more modifiers plus exactly one main key."""

    key: str
    modifiers: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {"key": self.key, "modifiers": list(self.modifiers)}

    def describe(self) -> str:
        return "+".join([*self.modifiers, self.key])


def _canonical_modifier_order(mods: Iterable[str]) -> tuple[str, ...]:
    """Stable modifier ordering so equal chords compare equal."""
    order = [MOD_CTRL, MOD_ALT, MOD_SHIFT, MOD_WIN]
    present = set(mods)
    return tuple(m for m in order if m in present)


def parse_chord(spec: str) -> Chord:
    """Parse a single chord such as ``"ctrl+s"`` or ``"f4"`` or ``"a"``.

    ``"+"`` and ``"^"`` are ambiguous — they are both separators and literal
    keys — so a trailing separator is read as the literal character, which is
    what ``"ctrl++"`` obviously means.
    """
    if not isinstance(spec, str) or not spec.strip():
        raise InvalidArguments("key chord must be a non-empty string",
                              details={"received": spec})
    raw = spec.strip()

    # Split on '+' but keep a trailing literal '+'.
    tokens: list[str] = []
    buffer = ""
    for index, char in enumerate(raw):
        if char == "+" and buffer:
            tokens.append(buffer)
            buffer = ""
        elif char == "+" and not buffer:
            # Separator with nothing before it => literal plus key.
            tokens.append("+")
        else:
            buffer += char
    if buffer:
        tokens.append(buffer)
    tokens = [t for t in tokens if t != ""]
    if not tokens:
        raise InvalidArguments("key chord contained no keys", details={"received": spec})

    modifiers: list[str] = []
    key: str | None = None
    for position, token in enumerate(tokens):
        lowered = token.strip().lower()
        is_last = position == len(tokens) - 1
        if not is_last:
            if lowered not in _MODIFIER_ALIASES:
                raise InvalidArguments(
                    f"{token!r} is not a modifier; only the final token may be a key",
                    details={"chord": spec, "token": token,
                             "supported_modifiers": sorted(set(_MODIFIER_ALIASES.values()))},
                )
            modifiers.append(_MODIFIER_ALIASES[lowered])
            continue
        # Final token: the main key.
        if lowered in _NAMED_KEYS:
            key = _NAMED_KEYS[lowered]
        elif len(token) == 1:
            key = token
        elif lowered in _MODIFIER_ALIASES:
            raise InvalidArguments(
                f"chord {spec!r} ends with modifier {token!r} and has no key",
                details={"chord": spec},
            )
        else:
            raise InvalidArguments(
                f"unknown key {token!r}",
                details={"chord": spec, "token": token,
                         "hint": "use a single character or a named key",
                         "named_keys": sorted(set(_NAMED_KEYS.values()))[:40]},
            )
    assert key is not None  # guaranteed by the loop above
    return Chord(key=key, modifiers=_canonical_modifier_order(modifiers))


def parse_keys(spec: str | Sequence[str]) -> list[Chord]:
    """Parse a chord sequence.

    Accepts either a list (``["ctrl+a", "delete"]``) or a single
    space-separated string (``"ctrl+a delete"``). The list form is preferred by
    planners; the string form is a convenience and cannot express a literal
    space key, which is why ``"space"`` is a named key.
    """
    if isinstance(spec, str):
        parts = [p for p in spec.split() if p]
    elif isinstance(spec, Sequence):
        parts = []
        for item in spec:
            if not isinstance(item, str):
                raise InvalidArguments(
                    "key sequence entries must be strings",
                    details={"received_type": type(item).__name__},
                )
            parts.append(item)
    else:
        raise InvalidArguments(
            "keys must be a string or list of strings",
            details={"received_type": type(spec).__name__},
        )
    if not parts:
        raise InvalidArguments("key sequence was empty", details={"received": spec})
    return [parse_chord(part) for part in parts]


def describe_keys(chords: Sequence[Chord]) -> str:
    return " ".join(c.describe() for c in chords)


__all__ = [
    "Chord", "parse_chord", "parse_keys", "describe_keys",
    "MOD_CTRL", "MOD_ALT", "MOD_SHIFT", "MOD_WIN",
]
