"""Pre- and post-conditions applied around interactions.

These implement the Manus findings that a lone operation handler cannot: they
need a *before* observation and an *after* observation, and they must fire
consistently across every operation rather than being remembered per handler.

Four guards, each answering a question a naive adapter never asks:

``elevation``
    Can this process actually drive the target, or is there an integrity
    boundary in the way? Asked *before* acting, so a UIPI failure is reported
    as a boundary rather than as a mysterious ``SendInput`` error.
``uac``
    Is a consent prompt on screen? If so, stop — this adapter never drives
    consent UI.
``foreground``
    Did focus stay with the same *process* across the input? If not, the
    keystrokes may have landed somewhere else entirely and the outcome is
    unknown, not merely failed.
``modal``
    Did a dialog appear that the action did not declare? If so, stop before
    pushing more input at whatever is now in front.

All of them are platform-free: they read :class:`~.model.WindowInfo` and ask
the backend for integrity levels, so they are exercised by the unit suite.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from .errors import (
    ElevationRequired,
    ForegroundChanged,
    UacPromptDetected,
    UnexpectedModal,
)
from .model import WindowInfo, integrity_rank


@dataclass(frozen=True)
class DesktopSnapshot:
    """The window state observed at one instant.

    Cheap enough to take immediately before and after every input event, which
    is the point: a guard that costs a full control-tree walk would not be
    taken often enough to catch anything.
    """

    foreground: WindowInfo | None
    windows: tuple[WindowInfo, ...]

    @property
    def handles(self) -> frozenset[int]:
        return frozenset(w.handle for w in self.windows)

    def window(self, handle: int) -> WindowInfo | None:
        for candidate in self.windows:
            if candidate.handle == handle:
                return candidate
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "foreground": self.foreground.to_dict() if self.foreground else None,
            "window_count": len(self.windows),
        }


def snapshot_desktop(backend: Any) -> DesktopSnapshot:
    """Observe foreground and window set. Never raises."""
    try:
        foreground = backend.foreground_window()
    except Exception:
        foreground = None
    try:
        windows = tuple(backend.list_windows(visible_only=True))
    except Exception:
        windows = ()
    return DesktopSnapshot(foreground=foreground, windows=windows)


# --- elevation / UAC ------------------------------------------------------

def check_uac(snapshot: DesktopSnapshot) -> None:
    """Stop if a UAC consent prompt is present.

    Deliberately not "dismiss it" or "click Yes". Approving an elevation
    request is a human decision, and an automation that can click through UAC
    is an automation that can silently escalate its own privileges. The only
    correct behaviour is to stop and say so.
    """
    for window in snapshot.windows:
        if window.is_uac_prompt:
            raise UacPromptDetected(
                f"UAC consent prompt is on screen ({window.process_name}); "
                "this adapter does not interact with consent UI",
                details={
                    "window": window.to_dict(),
                    "policy": "no automatic UAC handling; a human must respond",
                },
            )
    if snapshot.foreground is not None and snapshot.foreground.is_uac_prompt:
        raise UacPromptDetected(
            "UAC consent prompt holds foreground focus",
            details={"window": snapshot.foreground.to_dict()},
        )


def check_elevation(backend: Any, window: WindowInfo | None) -> dict[str, Any]:
    """Verify this process can drive ``window``, or escalate.

    Returns a decision record for evidence. Raises
    :class:`~.errors.ElevationRequired` when the target sits at a higher
    integrity level, because no amount of retrying crosses that boundary — the
    operator has to restart Pilot to match.
    """
    decision: dict[str, Any] = {"checked": False}
    if window is None:
        return decision

    caps = backend.capabilities()
    if not getattr(caps, "integrity_levels", False):
        # Say so rather than assuming parity: an unverified boundary is a known
        # unknown, and a mission log should show which it was.
        decision["reason"] = "backend cannot read integrity levels"
        return decision

    try:
        ours = backend.current_integrity()
        theirs = window.integrity_level or backend.process_integrity(window.process_id)
    except Exception as exc:
        decision["reason"] = f"integrity read failed: {type(exc).__name__}: {exc}"
        return decision

    decision.update({"checked": True, "self": ours, "target": theirs})
    our_rank, their_rank = integrity_rank(ours), integrity_rank(theirs)
    decision["self_rank"] = our_rank
    decision["target_rank"] = their_rank

    if their_rank > our_rank >= 0:
        raise ElevationRequired(
            f"target process {window.process_name or window.process_id} runs at "
            f"integrity {theirs!r} but this process is {ours!r}; Windows UIPI "
            "blocks input and inspection across that boundary",
            details={
                **decision,
                "window": window.to_dict(),
                "remedy": "restart the Pilot operator at a matching integrity "
                          "level; this adapter will not attempt to elevate",
            },
        )
    if their_rank < 0 and our_rank >= 0:
        # Could not read the target. Often exactly what an integrity boundary
        # looks like from below, so it is recorded as suspicious rather than
        # silently passed.
        decision["warning"] = (
            "target integrity level could not be read, which is itself a "
            "common symptom of an integrity boundary"
        )
    return decision


# --- foreground identity --------------------------------------------------

def check_foreground_stable(before: DesktopSnapshot, after: DesktopSnapshot,
                            *, context: str) -> dict[str, Any]:
    """Verify focus did not move to a different *process* across an input.

    Process identity, not window identity, is the right comparison. An
    application opening its own dialog moves the foreground window
    legitimately — that case belongs to the modal guard. Focus moving to
    another process while we were synthesising input means the input may have
    gone somewhere unintended, and the honest report is "outcome unknown".
    """
    record: dict[str, Any] = {
        "before": before.foreground.to_dict() if before.foreground else None,
        "after": after.foreground.to_dict() if after.foreground else None,
        "stable": True,
    }
    if before.foreground is None or after.foreground is None:
        # No foreground either side: nothing to compare, and an idle desktop is
        # not evidence of theft.
        record["stable"] = before.foreground is None and after.foreground is None
        record["note"] = "foreground absent on one side; not treated as theft"
        return record

    same_process = (before.foreground.process_id == after.foreground.process_id)
    record["stable"] = same_process
    record["same_window"] = before.foreground.handle == after.foreground.handle
    if same_process:
        return record

    raise ForegroundChanged(
        f"foreground moved from {before.foreground.process_name!r} "
        f"(pid {before.foreground.process_id}) to "
        f"{after.foreground.process_name!r} (pid {after.foreground.process_id}) "
        f"during {context}; synthesised input may have been delivered to the "
        "wrong application",
        details={
            **record,
            "context": context,
            "guidance": "establish what the input did before retrying; "
                        "re-discover state rather than repeating blindly",
        },
    )


# --- unexpected modals ----------------------------------------------------

def _is_modal_like(window: WindowInfo) -> bool:
    return bool(window.is_modal or window.is_dialog_class)


def check_no_unexpected_modal(before: DesktopSnapshot, after: DesktopSnapshot,
                              *, expected_titles: Sequence[str] = (),
                              allow_modals: bool = False,
                              context: str = "") -> dict[str, Any]:
    """Stop if a dialog appeared that the action did not declare.

    An undeclared dialog means the application asked something the mission did
    not anticipate — an overwrite confirmation, an error, an autosave prompt.
    Pressing on would aim the next action at a window nobody planned for, so
    execution stops here and the planner decides.

    Declaring the dialog (via ``expect.window_title`` or ``allow_modals``) is
    what makes an intended one — Save As after ctrl+s — legitimate.
    """
    new_windows = [w for w in after.windows if w.handle not in before.handles]
    new_modals = [w for w in new_windows if _is_modal_like(w)]
    record: dict[str, Any] = {
        "new_windows": [w.to_dict() for w in new_windows],
        "new_modals": [w.to_dict() for w in new_modals],
        "expected_titles": list(expected_titles),
        "allow_modals": allow_modals,
    }
    if not new_modals or allow_modals:
        record["blocked"] = False
        return record

    wanted = [t.casefold() for t in expected_titles if t]
    unexpected = [
        w for w in new_modals
        if not any(t in (w.title or "").casefold() or
                   (w.title or "").casefold() in t for t in wanted)
    ]
    record["unexpected_modals"] = [w.to_dict() for w in unexpected]
    record["blocked"] = bool(unexpected)
    if not unexpected:
        return record

    titles = ", ".join(repr(w.title) for w in unexpected)
    raise UnexpectedModal(
        f"unexpected dialog appeared during {context or 'the action'}: {titles}",
        details={
            **record,
            "context": context,
            "guidance": "handle the dialog explicitly, or re-issue the action "
                        "declaring it via expect.window_title / allow_modals",
        },
    )


__all__ = [
    "DesktopSnapshot",
    "snapshot_desktop",
    "check_uac",
    "check_elevation",
    "check_foreground_stable",
    "check_no_unexpected_modal",
]
