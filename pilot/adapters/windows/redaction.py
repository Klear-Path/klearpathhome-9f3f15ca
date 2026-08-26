"""Secret handling for evidence payloads (Manus finding: artifacts may contain secrets).

Two distinct problems, handled separately:

**Control values.** UIA hands back whatever a control holds. Most password
boxes mask their ValuePattern, but that is provider behaviour, not a
guarantee — and plenty of non-password fields hold API keys, tokens, and
connection strings. Evidence and error payloads are written to mission logs
that outlive the run, so values from controls that *look* sensitive are
replaced before they get there.

**Screenshots.** A screenshot cannot be redacted after the fact by anything
this module can do; whatever was on screen is in the PNG. So screenshots are
not sanitised, they are *labelled*: every capture carries a
``contains_untrusted_pixels`` marker so downstream storage can apply the right
retention and access policy, and capture stays opt-in per adapter.

This is deliberately conservative — over-redacting a field costs a planner
some diagnostic detail, while under-redacting one writes a credential into a
log permanently.
"""

from __future__ import annotations

import re
from typing import Any

#: Replacement marker. Distinctive so it is obvious in a log that redaction
#: happened, rather than looking like an empty field.
REDACTED = "<redacted:sensitive>"

#: Substrings in a control's name / automation id / class that mark it as
#: holding a secret. Matched case-insensitively against all three.
SENSITIVE_NAME_HINTS = (
    "password", "passwd", "pwd", "passphrase",
    "secret", "token", "api key", "apikey", "api_key",
    "credential", "private key", "privatekey",
    "pin", "cvv", "security code",
    "connection string", "connectionstring",
    "auth", "bearer", "session key",
)

#: Windows control classes used for masked input.
SENSITIVE_CLASS_HINTS = ("passwordbox", "passwordedit")

#: Values matching these shapes are redacted regardless of the control's
#: labelling — a token pasted into a plain text box is still a token.
_VALUE_PATTERNS = (
    # JWT
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+"),
    # Common provider key prefixes (GitHub, Slack, Stripe, AWS, OpenAI-style).
    re.compile(r"\b(?:gh[pousr]_|xox[baprs]-|sk-|pk_live_|rk_live_|AKIA)[A-Za-z0-9_-]{12,}"),
    # PEM private key blocks.
    re.compile(r"-----BEGIN[A-Z ]*PRIVATE KEY-----"),
    # URL with inline credentials.
    re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s/:@]+:[^\s/@]+@"),
)


def is_sensitive_control(*, name: str = "", automation_id: str = "",
                         class_name: str = "") -> bool:
    """Whether a control's identity marks it as holding a secret."""
    haystack = " ".join([name or "", automation_id or ""]).casefold()
    if any(hint in haystack for hint in SENSITIVE_NAME_HINTS):
        return True
    lowered_class = (class_name or "").casefold()
    return any(hint in lowered_class for hint in SENSITIVE_CLASS_HINTS)


def value_looks_secret(value: str | None) -> bool:
    """Whether a value's *shape* marks it as a credential."""
    if not value or not isinstance(value, str):
        return False
    return any(pattern.search(value) for pattern in _VALUE_PATTERNS)


def redact_value(value: str | None, *, name: str = "", automation_id: str = "",
                 class_name: str = "") -> str | None:
    """Redact a control value if either its control or its shape is sensitive."""
    if value is None:
        return None
    if is_sensitive_control(name=name, automation_id=automation_id,
                            class_name=class_name):
        return REDACTED
    if value_looks_secret(value):
        return REDACTED
    return value


def redact_text(text: str | None) -> str | None:
    """Redact a free-standing string (typed text, an expected value).

    Used for payloads the planner supplied rather than read from a control, so
    only shape-based detection applies.
    """
    if text is None:
        return None
    return REDACTED if value_looks_secret(text) else text


def redact_element_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Redact the value inside a serialised :class:`~.model.ElementSnapshot`.

    Returns a new dict; the caller's payload is not mutated. Adds
    ``value_redacted`` so a reader can tell a redacted field from an empty one.
    """
    if not isinstance(payload, dict) or "value" not in payload:
        return payload
    cleaned = dict(payload)
    original = cleaned.get("value")
    replaced = redact_value(
        original,
        name=cleaned.get("name") or "",
        automation_id=cleaned.get("automation_id") or "",
        class_name=cleaned.get("class_name") or "",
    )
    cleaned["value"] = replaced
    if original is not None and replaced == REDACTED and original != REDACTED:
        cleaned["value_redacted"] = True
    if isinstance(cleaned.get("children"), list):
        cleaned["children"] = [redact_element_payload(child)
                               for child in cleaned["children"]]
    return cleaned


def redact_tree_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Redact a summarised control-tree listing."""
    return [redact_element_payload(row) for row in rows]


#: Attached to every screenshot record. Screenshots cannot be redacted after
#: capture, so they are labelled for downstream retention policy instead.
SCREENSHOT_SENSITIVITY_NOTE = (
    "screenshot may contain credentials, personal data, or other secrets "
    "visible on screen at capture time; treat as sensitive at rest"
)


def screenshot_record(path: str, *, label: str) -> dict[str, Any]:
    """Describe a captured screenshot, carrying its sensitivity marker."""
    return {
        "path": path,
        "label": label,
        "contains_untrusted_pixels": True,
        "sensitivity": SCREENSHOT_SENSITIVITY_NOTE,
    }


__all__ = [
    "REDACTED",
    "SENSITIVE_NAME_HINTS",
    "SCREENSHOT_SENSITIVITY_NOTE",
    "is_sensitive_control",
    "value_looks_secret",
    "redact_value",
    "redact_text",
    "redact_element_payload",
    "redact_tree_rows",
    "screenshot_record",
]
