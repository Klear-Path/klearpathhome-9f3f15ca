"""Windows implementation of :class:`~.backend.UiaBackend`.

Import fails loudly off Windows; :func:`~.adapter.default_backend` catches
that and substitutes :class:`~.backend.NullBackend`, so nothing above this
module needs a platform guard.

Layering, matching the lane's execution preference:

* **UI Automation** (via the ``uiautomation`` package, which wraps the native
  ``IUIAutomation`` COM interfaces through ``comtypes``) for the control tree
  and every pattern-based interaction. This is the primary path.
* **Win32 directly, through ctypes** for window enumeration, foreground
  detection, focus changes, and synthetic input. ``SendInput`` is used rather
  than the ``uiautomation`` package's own ``SendKeys`` DSL so that chord
  handling stays in :mod:`.keyboard`, where it is unit-tested, instead of
  being re-parsed by a third-party string mini-language.
* **Coordinate clicking** last, and only when an operation explicitly asks.

Live COM elements are not stored in :class:`~.model.ElementSnapshot` (which
must stay picklable and platform-free). Instead each walk records
``runtime_id -> Control`` in a bounded cache; interactions look the element up
there and fall back to re-resolving by runtime id if it has been evicted.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import time
from ctypes import wintypes
from typing import Any, Sequence

if sys.platform != "win32":  # pragma: no cover - import guard
    raise ImportError(
        f"pilot.adapters.windows.uia_backend requires Windows; host is {sys.platform!r}"
    )

import uiautomation as auto  # type: ignore[import-not-found]

from .backend import BackendCapabilities
from .errors import (
    BackendError,
    ElementNotFound,
    ElementNotInteractable,
    LaunchFailed,
    UnsupportedUi,
    WindowNotFound,
)
from .keyboard import Chord, MOD_ALT, MOD_CTRL, MOD_SHIFT, MOD_WIN
from .model import (
    DIALOG_CLASS_NAMES,
    PATTERN_EXPAND_COLLAPSE,
    PATTERN_INVOKE,
    PATTERN_LEGACY_IACCESSIBLE,
    PATTERN_SELECTION_ITEM,
    PATTERN_TEXT,
    PATTERN_TOGGLE,
    PATTERN_VALUE,
    PATTERN_WINDOW,
    ElementSnapshot,
    Rect,
    WindowInfo,
)

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)


class _SID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Sid", ctypes.c_void_p), ("Attributes", wintypes.DWORD)]

_ENUM_PROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def _declare_prototypes() -> None:
    """Pin argtypes/restypes for every Win32 call this backend makes.

    Not optional tidiness. ctypes defaults an undeclared return type to
    ``c_int``, which silently truncates a 64-bit ``HWND`` on x64 and
    misinterprets the signed ``SHORT`` that ``VkKeyScanW`` returns. Both
    produce wrong-but-plausible values rather than errors, so they are declared
    explicitly instead of trusted to the default.
    """
    user32.EnumWindows.argtypes = [_ENUM_PROC, wintypes.LPARAM]
    user32.EnumWindows.restype = wintypes.BOOL
    user32.GetForegroundWindow.argtypes = []
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.IsWindow.argtypes = [wintypes.HWND]
    user32.IsWindow.restype = wintypes.BOOL
    user32.IsIconic.argtypes = [wintypes.HWND]
    user32.IsIconic.restype = wintypes.BOOL
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.ShowWindow.restype = wintypes.BOOL
    user32.SetForegroundWindow.argtypes = [wintypes.HWND]
    user32.SetForegroundWindow.restype = wintypes.BOOL
    user32.BringWindowToTop.argtypes = [wintypes.HWND]
    user32.BringWindowToTop.restype = wintypes.BOOL
    user32.SetActiveWindow.argtypes = [wintypes.HWND]
    user32.SetActiveWindow.restype = wintypes.HWND
    user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
    user32.AttachThreadInput.restype = wintypes.BOOL
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND,
                                               ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.GetWindowRect.restype = wintypes.BOOL
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.restype = ctypes.c_int
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetClassNameW.restype = ctypes.c_int
    user32.GetSystemMetrics.argtypes = [ctypes.c_int]
    user32.GetSystemMetrics.restype = ctypes.c_int
    user32.SendInput.argtypes = [wintypes.UINT, ctypes.c_void_p, ctypes.c_int]
    user32.SendInput.restype = wintypes.UINT
    # The one that matters most: a signed SHORT carrying the shift state in its
    # high byte and -1 for "no such key on this layout".
    user32.VkKeyScanW.argtypes = [ctypes.c_wchar]
    user32.VkKeyScanW.restype = ctypes.c_short
    user32.SetProcessDPIAware.argtypes = []
    user32.SetProcessDPIAware.restype = wintypes.BOOL

    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD)]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel32.GetCurrentThreadId.argtypes = []
    kernel32.GetCurrentThreadId.restype = wintypes.DWORD
    kernel32.GetCurrentProcess.argtypes = []
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE

    user32.GetWindow.argtypes = [wintypes.HWND, wintypes.UINT]
    user32.GetWindow.restype = wintypes.HWND
    user32.IsWindowEnabled.argtypes = [wintypes.HWND]
    user32.IsWindowEnabled.restype = wintypes.BOOL
    # GetWindowLongPtrW is 64-bit only; the 32-bit build exposes GetWindowLongW.
    _get_long = getattr(user32, "GetWindowLongPtrW", None) or user32.GetWindowLongW
    _get_long.argtypes = [wintypes.HWND, ctypes.c_int]
    _get_long.restype = ctypes.c_ssize_t
    if not hasattr(user32, "GetWindowLongPtrW"):
        user32.GetWindowLongPtrW = _get_long

    advapi32.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                          ctypes.POINTER(wintypes.HANDLE)]
    advapi32.OpenProcessToken.restype = wintypes.BOOL
    advapi32.GetTokenInformation.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p,
        wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    advapi32.GetTokenInformation.restype = wintypes.BOOL
    advapi32.GetSidSubAuthorityCount.argtypes = [ctypes.c_void_p]
    advapi32.GetSidSubAuthorityCount.restype = ctypes.c_void_p
    advapi32.GetSidSubAuthority.argtypes = [ctypes.c_void_p, wintypes.DWORD]
    advapi32.GetSidSubAuthority.restype = ctypes.c_void_p


_declare_prototypes()


def _foreground_hwnd() -> int:
    """The foreground window handle, or 0 when nothing has focus.

    Normalises the ``HWND`` restype, which ctypes surfaces as ``None`` for
    NULL — an int keeps every comparison site simple.
    """
    handle = user32.GetForegroundWindow()
    return int(handle) if handle else 0

# --- Win32 constants -------------------------------------------------------

SW_RESTORE = 9
SW_SHOW = 5
WM_CLOSE = 0x0010

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
TOKEN_QUERY = 0x0008
TokenIntegrityLevel = 25

#: Integrity-level RIDs, per Windows' SID authority scheme.
SECURITY_MANDATORY_UNTRUSTED_RID = 0x0000
SECURITY_MANDATORY_LOW_RID = 0x1000
SECURITY_MANDATORY_MEDIUM_RID = 0x2000
SECURITY_MANDATORY_MEDIUM_PLUS_RID = 0x2100
SECURITY_MANDATORY_HIGH_RID = 0x3000
SECURITY_MANDATORY_SYSTEM_RID = 0x4000

GW_OWNER = 4
GWL_EXSTYLE = -20
WS_EX_DLGMODALFRAME = 0x00000001
WS_EX_TOPMOST = 0x00000008

#: Virtual-key codes for this lane's canonical named keys (see .keyboard).
VK_MAP: dict[str, int] = {
    "enter": 0x0D, "tab": 0x09, "escape": 0x1B, "space": 0x20,
    "backspace": 0x08, "delete": 0x2E, "insert": 0x2D,
    "home": 0x24, "end": 0x23, "page_up": 0x21, "page_down": 0x22,
    "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
    "print_screen": 0x2C, "caps_lock": 0x14, "num_lock": 0x90,
    "scroll_lock": 0x91, "pause": 0x13, "apps": 0x5D,
}
for _i in range(1, 25):
    VK_MAP[f"f{_i}"] = 0x6F + _i  # VK_F1 == 0x70

MODIFIER_VK = {
    MOD_CTRL: 0x11,   # VK_CONTROL
    MOD_ALT: 0x12,    # VK_MENU
    MOD_SHIFT: 0x10,  # VK_SHIFT
    MOD_WIN: 0x5B,    # VK_LWIN
}

#: Keys on the extended-key half of the keyboard. Omitting the extended flag
#: makes arrow keys and Delete behave as their numpad twins, which silently
#: corrupts navigation.
EXTENDED_KEYS = {
    "up", "down", "left", "right", "home", "end",
    "page_up", "page_down", "insert", "delete",
    "print_screen", "num_lock", "apps",
}


# --- SendInput structures --------------------------------------------------

class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG), ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]


class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]


class _HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD)]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("mi", _MOUSEINPUT), ("ki", _KEYBDINPUT), ("hi", _HARDWAREINPUT)]


class _INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", _INPUTUNION)]


def _send_inputs(inputs: Sequence[_INPUT]) -> None:
    if not inputs:
        return
    array = (_INPUT * len(inputs))(*inputs)
    sent = user32.SendInput(len(inputs), ctypes.byref(array),
                            ctypes.sizeof(_INPUT))
    if sent != len(inputs):
        raise BackendError(
            f"SendInput delivered {sent}/{len(inputs)} events",
            details={"win32_error": ctypes.get_last_error(),
                     "hint": "a UIPI boundary (elevated window) usually causes this"},
        )


def _key_input(vk: int, *, up: bool, extended: bool = False) -> _INPUT:
    flags = 0
    if up:
        flags |= KEYEVENTF_KEYUP
    if extended:
        flags |= KEYEVENTF_EXTENDEDKEY
    return _INPUT(type=INPUT_KEYBOARD,
                  union=_INPUTUNION(ki=_KEYBDINPUT(wVk=vk, wScan=0, dwFlags=flags,
                                                   time=0, dwExtraInfo=None)))


def _unicode_input(char: str, *, up: bool) -> _INPUT:
    flags = KEYEVENTF_UNICODE | (KEYEVENTF_KEYUP if up else 0)
    return _INPUT(type=INPUT_KEYBOARD,
                  union=_INPUTUNION(ki=_KEYBDINPUT(wVk=0, wScan=ord(char),
                                                   dwFlags=flags, time=0,
                                                   dwExtraInfo=None)))


def _enable_dpi_awareness() -> str:
    """Opt into per-monitor DPI awareness.

    Without this, Win32 reports virtualised coordinates on scaled displays and
    every coordinate click lands in the wrong place. Best-effort: the call
    fails harmlessly if the host already set an awareness context.
    """
    try:
        # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 == -4
        if user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4)):
            return "per_monitor_v2"
    except AttributeError:
        pass
    try:
        shcore = ctypes.WinDLL("shcore")
        if shcore.SetProcessDpiAwareness(2) == 0:  # PROCESS_PER_MONITOR_DPI_AWARE
            return "per_monitor"
    except Exception:
        pass
    try:
        if user32.SetProcessDPIAware():
            return "system"
    except Exception:
        pass
    return "unknown"


def _process_name(process_id: int) -> str:
    """Executable basename for a pid, or '' if it cannot be read."""
    if not process_id:
        return ""
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, process_id)
    if not handle:
        return ""
    try:
        size = wintypes.DWORD(1024)
        buffer = ctypes.create_unicode_buffer(size.value)
        if kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
            return os.path.basename(buffer.value)
        return ""
    finally:
        kernel32.CloseHandle(handle)


def _rid_to_integrity(rid: int) -> str:
    """Map a mandatory-label RID onto this lane's integrity vocabulary."""
    if rid >= SECURITY_MANDATORY_SYSTEM_RID:
        return "system"
    if rid >= SECURITY_MANDATORY_HIGH_RID:
        return "high"
    if rid >= SECURITY_MANDATORY_MEDIUM_PLUS_RID:
        return "medium_plus"
    if rid >= SECURITY_MANDATORY_MEDIUM_RID:
        return "medium"
    if rid >= SECURITY_MANDATORY_LOW_RID:
        return "low"
    return "untrusted"


def _token_integrity(token: int) -> str:
    """Read a token's integrity level, or "" when it cannot be determined."""
    size = wintypes.DWORD(0)
    advapi32.GetTokenInformation(wintypes.HANDLE(token), TokenIntegrityLevel,
                                 None, 0, ctypes.byref(size))
    if not size.value:
        return ""
    buffer = ctypes.create_string_buffer(size.value)
    if not advapi32.GetTokenInformation(wintypes.HANDLE(token), TokenIntegrityLevel,
                                        buffer, size, ctypes.byref(size)):
        return ""
    # TOKEN_MANDATORY_LABEL is a SID_AND_ATTRIBUTES; the level lives in the
    # SID's last sub-authority.
    label = ctypes.cast(buffer, ctypes.POINTER(_SID_AND_ATTRIBUTES)).contents
    count_ptr = advapi32.GetSidSubAuthorityCount(label.Sid)
    if not count_ptr:
        return ""
    count = ctypes.cast(count_ptr, ctypes.POINTER(ctypes.c_ubyte)).contents.value
    if count == 0:
        return ""
    rid_ptr = advapi32.GetSidSubAuthority(label.Sid, count - 1)
    if not rid_ptr:
        return ""
    rid = ctypes.cast(rid_ptr, ctypes.POINTER(wintypes.DWORD)).contents.value
    return _rid_to_integrity(int(rid))


def _process_integrity(process_id: int) -> str:
    """Integrity level of a process, or "" when unreadable.

    Unreadable is a meaningful answer, not a failure: being unable to open a
    process token is itself a common symptom of an integrity boundary, and the
    guard layer treats "" as suspicious rather than equal.
    """
    if not process_id:
        return ""
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False,
                                  process_id)
    if not handle:
        return ""
    token = wintypes.HANDLE()
    try:
        if not advapi32.OpenProcessToken(handle, TOKEN_QUERY, ctypes.byref(token)):
            return ""
        try:
            return _token_integrity(token.value)
        finally:
            kernel32.CloseHandle(token)
    finally:
        kernel32.CloseHandle(handle)


def _is_modal_window(hwnd: int) -> bool:
    """Whether a window looks modal.

    Three signals, any of which is enough: the classic dialog window class, a
    modal frame extended style, or an owner window that is currently disabled
    (which is how Windows actually enforces modality).
    """
    if _window_class(hwnd).strip().lower() in DIALOG_CLASS_NAMES:
        return True
    try:
        ex_style = user32.GetWindowLongPtrW(wintypes.HWND(hwnd), GWL_EXSTYLE)
        if int(ex_style) & WS_EX_DLGMODALFRAME:
            return True
    except Exception:
        pass
    owner = user32.GetWindow(wintypes.HWND(hwnd), GW_OWNER)
    if owner and not user32.IsWindowEnabled(wintypes.HWND(owner)):
        # The owner being disabled while this window is up is the definition
        # of a modal dialog on Win32.
        return True
    return False


def _window_rect(hwnd: int) -> Rect:
    rect = wintypes.RECT()
    if not user32.GetWindowRect(wintypes.HWND(hwnd), ctypes.byref(rect)):
        return Rect()
    return Rect(left=rect.left, top=rect.top, right=rect.right, bottom=rect.bottom)


def _window_title(hwnd: int) -> str:
    length = user32.GetWindowTextLengthW(wintypes.HWND(hwnd))
    if length <= 0:
        return ""
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(wintypes.HWND(hwnd), buffer, length + 1)
    return buffer.value


def _window_class(hwnd: int) -> str:
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(wintypes.HWND(hwnd), buffer, 256)
    return buffer.value


def _window_pid(hwnd: int) -> int:
    pid = wintypes.DWORD(0)
    user32.GetWindowThreadProcessId(wintypes.HWND(hwnd), ctypes.byref(pid))
    return int(pid.value)


def _describe_window(hwnd: int, *, foreground: int | None = None,
                     with_integrity: bool = True) -> WindowInfo:
    pid = _window_pid(hwnd)
    return WindowInfo(
        handle=int(hwnd),
        title=_window_title(hwnd),
        process_id=pid,
        process_name=_process_name(pid),
        class_name=_window_class(hwnd),
        rect=_window_rect(hwnd),
        is_foreground=(int(hwnd) == (foreground if foreground is not None
                                     else _foreground_hwnd())),
        is_minimized=bool(user32.IsIconic(wintypes.HWND(hwnd))),
        is_visible=bool(user32.IsWindowVisible(wintypes.HWND(hwnd))),
        is_modal=_is_modal_window(hwnd),
        # Opening a token per window is not free, so enumeration can skip it;
        # the guard layer falls back to process_integrity() on demand.
        integrity_level=_process_integrity(pid) if with_integrity else "",
    )


class UiaWindowsBackend:
    """Live Windows backend.

    Instances are not thread-safe: UIA COM objects are apartment-bound, and
    the ``uiautomation`` package initialises COM per thread. Construct one per
    worker thread.
    """

    def __init__(self, *, element_cache_size: int = 4096) -> None:
        self._dpi_mode = _enable_dpi_awareness()
        # Suppress the package's own console chatter and auto-search retries;
        # this lane does its own waiting, with its own deadlines.
        auto.uiautomation.DEBUG_SEARCH_TIME = False
        auto.SetGlobalSearchTimeout(0.0)
        self._cache: dict[str, Any] = {}
        self._cache_order: list[str] = []
        self._cache_size = element_cache_size
        self._screenshot_backend = self._detect_screenshot_backend()
        #: Cached because this process's own integrity cannot change while it
        #: runs, and the guards consult it on every input event.
        self._own_integrity: str | None = None

    # --- capabilities ---------------------------------------------------

    @staticmethod
    def _detect_screenshot_backend() -> str | None:
        # Import-probe only; Pillow is an optional extra, and its absence
        # degrades screenshots rather than breaking the backend.
        import importlib.util

        try:
            if importlib.util.find_spec("PIL.ImageGrab") is not None:
                return "pillow"
        except (ImportError, ValueError):
            pass
        return None

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            name="windows_uia",
            platform="win32",
            ui_automation=True,
            keyboard=True,
            mouse=True,
            screenshots=self._screenshot_backend is not None,
            process_launch=True,
            window_management=True,
            vision=False,
            integrity_levels=True,
            notes=f"uiautomation={getattr(auto, '__version__', 'unknown')} "
                  f"dpi={self._dpi_mode} "
                  f"screenshots={self._screenshot_backend or 'unavailable (install Pillow)'}",
        )

    # --- element cache --------------------------------------------------

    def _remember(self, runtime_id: str, control: Any) -> None:
        if runtime_id in self._cache:
            return
        self._cache[runtime_id] = control
        self._cache_order.append(runtime_id)
        while len(self._cache_order) > self._cache_size:
            evicted = self._cache_order.pop(0)
            self._cache.pop(evicted, None)

    def _control_for(self, element: ElementSnapshot) -> Any:
        control = self._cache.get(element.runtime_id)
        if control is not None:
            return control
        # Evicted or from an older walk: re-walk the owning window and look the
        # runtime id up again rather than failing.
        if element.window_handle:
            self.control_tree(window_handle=element.window_handle, max_depth=16)
            control = self._cache.get(element.runtime_id)
        if control is None:
            raise ElementNotFound(
                f"element {element.runtime_id} is no longer available; "
                "the UI has probably changed",
                details={"element": element.to_dict(include_children=False)},
            )
        return control

    # --- windows --------------------------------------------------------

    def list_windows(self, *, visible_only: bool = True) -> list[WindowInfo]:
        handles: list[int] = []

        def _collect(hwnd, _lparam):
            handles.append(int(hwnd))
            return True

        if not user32.EnumWindows(_ENUM_PROC(_collect), 0):
            # EnumWindows returns false if the callback stopped early; we never
            # stop early, so treat it as a real failure.
            error = ctypes.get_last_error()
            if error:
                raise BackendError("EnumWindows failed",
                                   details={"win32_error": error})

        foreground = _foreground_hwnd()
        windows: list[WindowInfo] = []
        for hwnd in handles:
            if visible_only:
                if not user32.IsWindowVisible(wintypes.HWND(hwnd)):
                    continue
                # A visible window with no title is nearly always an invisible
                # helper (IME hosts, tooltips, shell surfaces). Excluding them
                # keeps enumeration usable for a planner.
                if not _window_title(hwnd):
                    continue
            windows.append(_describe_window(hwnd, foreground=foreground,
                                            with_integrity=False))
        return windows

    def foreground_window(self) -> WindowInfo | None:
        hwnd = _foreground_hwnd()
        if not hwnd:
            return None
        return _describe_window(hwnd, foreground=hwnd)

    def focus_window(self, handle: int) -> WindowInfo:
        hwnd = wintypes.HWND(int(handle))
        if not user32.IsWindow(hwnd):
            raise WindowNotFound(f"handle {handle} is not a window",
                                 details={"handle": handle})
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, SW_RESTORE)
        else:
            user32.ShowWindow(hwnd, SW_SHOW)

        # SetForegroundWindow is refused unless the calling process already owns
        # the foreground or is otherwise privileged. Attaching to the target's
        # input queue is the documented cooperative workaround; we then verify
        # rather than assume, and let the operation layer report a real failure
        # if focus did not move.
        target_thread = user32.GetWindowThreadProcessId(hwnd, None)
        our_thread = kernel32.GetCurrentThreadId()
        attached = False
        if target_thread and target_thread != our_thread:
            attached = bool(user32.AttachThreadInput(our_thread, target_thread, True))
        try:
            for attempt in range(3):
                user32.SetForegroundWindow(hwnd)
                user32.BringWindowToTop(hwnd)
                user32.SetActiveWindow(hwnd)
                if _foreground_hwnd() == int(handle):
                    break
                time.sleep(0.08 * (attempt + 1))
        finally:
            if attached:
                user32.AttachThreadInput(our_thread, target_thread, False)

        return _describe_window(int(handle))

    # --- process --------------------------------------------------------

    def launch(self, command: str, *, arguments: Sequence[str] = (),
               working_directory: str | None = None,
               wait_for_window_seconds: float = 10.0) -> tuple[int, WindowInfo | None]:
        argv = [command, *arguments]
        try:
            # shell=False on purpose: no shell metacharacter interpretation, so
            # a crafted application name cannot become a command line.
            process = subprocess.Popen(
                argv, cwd=working_directory, shell=False,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            raise
        except OSError as exc:
            raise LaunchFailed(f"could not start {command!r}: {exc}",
                               details={"command": command,
                                        "arguments": list(arguments)}) from exc

        pid = process.pid
        deadline = time.monotonic() + max(0.0, wait_for_window_seconds)
        while time.monotonic() < deadline:
            # Match on the whole process tree, not just `pid`: many stock
            # Windows apps (Calculator, Settings) are launcher stubs whose real
            # UI belongs to a different process.
            for window in self.list_windows(visible_only=True):
                if window.process_id == pid:
                    return pid, window
            if process.poll() is not None:
                break
            time.sleep(0.15)

        # Fall back to a name match: the stub case above.
        expected = os.path.splitext(os.path.basename(command))[0].casefold()
        for window in self.list_windows(visible_only=True):
            stem = os.path.splitext(window.process_name)[0].casefold()
            if stem and (stem == expected or expected in stem):
                return pid, window
        return pid, None

    # --- control tree ---------------------------------------------------

    @staticmethod
    def _patterns_for(control: Any) -> tuple[str, ...]:
        """Which accessible patterns an element advertises.

        Probed by asking for each pattern object: ``IsPatternAvailable`` is not
        uniformly reliable across providers, whereas a successful ``GetPattern``
        is proof the interaction will be attempted against something real.
        """
        found: list[str] = []
        probes = (
            (PATTERN_INVOKE, auto.PatternId.InvokePattern),
            (PATTERN_VALUE, auto.PatternId.ValuePattern),
            (PATTERN_TEXT, auto.PatternId.TextPattern),
            (PATTERN_TOGGLE, auto.PatternId.TogglePattern),
            (PATTERN_EXPAND_COLLAPSE, auto.PatternId.ExpandCollapsePattern),
            (PATTERN_SELECTION_ITEM, auto.PatternId.SelectionItemPattern),
            (PATTERN_WINDOW, auto.PatternId.WindowPattern),
            (PATTERN_LEGACY_IACCESSIBLE, auto.PatternId.LegacyIAccessiblePattern),
        )
        for name, pattern_id in probes:
            try:
                if control.GetPattern(pattern_id) is not None:
                    found.append(name)
            except Exception:
                continue
        return tuple(found)

    @staticmethod
    def _value_of(control: Any, patterns: Sequence[str]) -> str | None:
        """Read a control's text, preferring ValuePattern then TextPattern."""
        if PATTERN_VALUE in patterns:
            try:
                pattern = control.GetPattern(auto.PatternId.ValuePattern)
                if pattern is not None:
                    return pattern.Value
            except Exception:
                pass
        if PATTERN_TEXT in patterns:
            try:
                pattern = control.GetPattern(auto.PatternId.TextPattern)
                if pattern is not None:
                    # Bounded: a document's full text can be enormous, and this
                    # is a state snapshot, not a file read.
                    return pattern.DocumentRange.GetText(65536)
            except Exception:
                pass
        return None

    def _snapshot(self, control: Any, depth: int, window_handle: int,
                  *, with_value: bool = True) -> ElementSnapshot:
        patterns = self._patterns_for(control)
        try:
            rect_raw = control.BoundingRectangle
            rect = Rect(left=int(rect_raw.left), top=int(rect_raw.top),
                        right=int(rect_raw.right), bottom=int(rect_raw.bottom))
        except Exception:
            rect = Rect()

        def _safe(getter, default):
            try:
                value = getter()
                return default if value is None else value
            except Exception:
                return default

        runtime = _safe(lambda: "-".join(str(x) for x in control.GetRuntimeId()), "")
        if not runtime:
            # No runtime id (rare, and a provider bug) — synthesise a stable-ish
            # one so the element is still addressable within this walk.
            runtime = f"synthetic:{window_handle}:{depth}:{id(control)}"

        snapshot = ElementSnapshot(
            runtime_id=runtime,
            name=_safe(lambda: control.Name, "") or "",
            role=_safe(lambda: control.ControlTypeName, "") or "",
            automation_id=_safe(lambda: control.AutomationId, "") or "",
            class_name=_safe(lambda: control.ClassName, "") or "",
            value=self._value_of(control, patterns) if with_value else None,
            enabled=bool(_safe(lambda: control.IsEnabled, True)),
            offscreen=bool(_safe(lambda: control.IsOffscreen, False)),
            focused=bool(_safe(lambda: control.HasKeyboardFocus, False)),
            keyboard_focusable=bool(_safe(lambda: control.IsKeyboardFocusable, False)),
            rect=rect,
            patterns=patterns,
            depth=depth,
            children=(),
            process_id=int(_safe(lambda: control.ProcessId, 0) or 0),
            window_handle=window_handle,
        )
        self._remember(snapshot.runtime_id, control)
        return snapshot

    def control_tree(self, *, window_handle: int | None = None,
                     max_depth: int = 12,
                     max_elements: int = 2000) -> ElementSnapshot:
        try:
            if window_handle:
                root_control = auto.ControlFromHandle(int(window_handle))
                if root_control is None:
                    raise WindowNotFound(
                        f"no UIA element for window handle {window_handle}",
                        details={"handle": window_handle},
                    )
            else:
                root_control = auto.GetRootControl()
        except WindowNotFound:
            raise
        except Exception as exc:
            raise BackendError(f"could not obtain UIA root: {exc}",
                               details={"handle": window_handle}) from exc

        handle = int(window_handle or 0)
        budget = {"remaining": max(1, max_elements)}

        def _build(control: Any, depth: int) -> ElementSnapshot:
            snapshot = self._snapshot(control, depth, handle)
            budget["remaining"] -= 1
            if depth >= max_depth or budget["remaining"] <= 0:
                return snapshot
            children: list[ElementSnapshot] = []
            try:
                child_controls = control.GetChildren()
            except Exception:
                # A provider that refuses to enumerate children is exactly the
                # inaccessible-UI case: keep the node, drop the subtree.
                child_controls = []
            for child in child_controls:
                if budget["remaining"] <= 0:
                    break
                try:
                    children.append(_build(child, depth + 1))
                except Exception:
                    continue
            return ElementSnapshot(
                runtime_id=snapshot.runtime_id, name=snapshot.name,
                role=snapshot.role, automation_id=snapshot.automation_id,
                class_name=snapshot.class_name, value=snapshot.value,
                enabled=snapshot.enabled, offscreen=snapshot.offscreen,
                focused=snapshot.focused,
                keyboard_focusable=snapshot.keyboard_focusable,
                rect=snapshot.rect, patterns=snapshot.patterns,
                depth=snapshot.depth, children=tuple(children),
                process_id=snapshot.process_id,
                window_handle=snapshot.window_handle,
            )

        return _build(root_control, 0)

    def refresh(self, element: ElementSnapshot) -> ElementSnapshot:
        control = self._control_for(element)
        return self._snapshot(control, element.depth, element.window_handle)

    # --- integrity & geometry -------------------------------------------

    def current_integrity(self) -> str:
        if self._own_integrity is None:
            token = wintypes.HANDLE()
            level = ""
            if advapi32.OpenProcessToken(kernel32.GetCurrentProcess(),
                                         TOKEN_QUERY, ctypes.byref(token)):
                try:
                    level = _token_integrity(token.value)
                finally:
                    kernel32.CloseHandle(token)
            self._own_integrity = level
        return self._own_integrity

    def process_integrity(self, process_id: int) -> str:
        return _process_integrity(int(process_id))

    def element_rect(self, element: ElementSnapshot) -> Rect:
        """Live bounding rectangle, read now rather than recalled.

        Deliberately minimal: one BoundingRectangle read, no pattern probing,
        no child enumeration. The value of this call is that the gap between
        reading the geometry and clicking it is as small as it can be.
        """
        control = self._control_for(element)
        try:
            raw = control.BoundingRectangle
        except Exception as exc:
            raise BackendError(
                f"could not read bounding rectangle: {exc}",
                details={"element": element.describe()}) from exc
        return Rect(left=int(raw.left), top=int(raw.top),
                    right=int(raw.right), bottom=int(raw.bottom))

    # --- interaction ----------------------------------------------------

    def _pattern_or_fail(self, element: ElementSnapshot, pattern_id: Any,
                         label: str) -> Any:
        control = self._control_for(element)
        try:
            pattern = control.GetPattern(pattern_id)
        except Exception as exc:
            raise BackendError(f"failed to get {label} pattern: {exc}",
                               details={"element": element.describe()}) from exc
        if pattern is None:
            raise UnsupportedUi(
                f"element does not support {label}: {element.describe()}",
                details={"element": element.to_dict(include_children=False),
                         "advertised_patterns": list(element.patterns)},
            )
        return pattern

    def invoke(self, element: ElementSnapshot) -> None:
        if PATTERN_INVOKE in element.patterns:
            pattern = self._pattern_or_fail(element, auto.PatternId.InvokePattern, "Invoke")
            try:
                pattern.Invoke()
                return
            except Exception as exc:
                raise BackendError(f"Invoke failed: {exc}",
                                   details={"element": element.describe()}) from exc
        # LegacyIAccessible.DoDefaultAction reaches older MSAA-only controls
        # (common in Win32 dialogs) that expose no InvokePattern.
        pattern = self._pattern_or_fail(
            element, auto.PatternId.LegacyIAccessiblePattern, "Invoke/DoDefaultAction")
        try:
            pattern.DoDefaultAction()
        except Exception as exc:
            raise BackendError(f"DoDefaultAction failed: {exc}",
                               details={"element": element.describe()}) from exc

    def set_value(self, element: ElementSnapshot, value: str) -> None:
        pattern = self._pattern_or_fail(element, auto.PatternId.ValuePattern, "Value")
        try:
            if pattern.IsReadOnly:
                raise ElementNotInteractable(
                    f"control is read-only: {element.describe()}",
                    details={"element": element.to_dict(include_children=False)},
                )
        except AttributeError:
            pass  # provider does not report read-only state
        try:
            pattern.SetValue(value)
        except Exception as exc:
            raise BackendError(f"SetValue failed: {exc}",
                               details={"element": element.describe(),
                                        "hint": "fall back to focus + type_text"}) from exc

    def focus_element(self, element: ElementSnapshot) -> None:
        control = self._control_for(element)
        try:
            control.SetFocus()
        except Exception as exc:
            raise ElementNotInteractable(
                f"could not focus {element.describe()}: {exc}",
                details={"element": element.to_dict(include_children=False)},
            ) from exc

    def toggle(self, element: ElementSnapshot) -> None:
        pattern = self._pattern_or_fail(element, auto.PatternId.TogglePattern, "Toggle")
        try:
            pattern.Toggle()
        except Exception as exc:
            raise BackendError(f"Toggle failed: {exc}",
                               details={"element": element.describe()}) from exc

    def select_item(self, element: ElementSnapshot) -> None:
        pattern = self._pattern_or_fail(
            element, auto.PatternId.SelectionItemPattern, "SelectionItem")
        try:
            pattern.Select()
        except Exception as exc:
            raise BackendError(f"Select failed: {exc}",
                               details={"element": element.describe()}) from exc

    def expand(self, element: ElementSnapshot, *, expand: bool = True) -> None:
        pattern = self._pattern_or_fail(
            element, auto.PatternId.ExpandCollapsePattern, "ExpandCollapse")
        try:
            pattern.Expand() if expand else pattern.Collapse()
        except Exception as exc:
            raise BackendError(f"{'Expand' if expand else 'Collapse'} failed: {exc}",
                               details={"element": element.describe()}) from exc

    # --- keyboard & mouse -----------------------------------------------

    def send_keys(self, chords: Sequence[Chord]) -> None:
        for chord in chords:
            events: list[_INPUT] = []
            modifier_vks = [MODIFIER_VK[m] for m in chord.modifiers]
            for vk in modifier_vks:
                events.append(_key_input(vk, up=False))

            key = chord.key
            if key in VK_MAP:
                vk = VK_MAP[key]
                extended = key in EXTENDED_KEYS
                events.append(_key_input(vk, up=False, extended=extended))
                events.append(_key_input(vk, up=True, extended=extended))
            elif len(key) == 1:
                # VkKeyScanW maps the character to a virtual key on the active
                # layout. A real VK (rather than a Unicode event) is required
                # for accelerators: ctrl+S must arrive as a chord, and a
                # KEYEVENTF_UNICODE 'S' would not trigger the menu.
                scan = user32.VkKeyScanW(ctypes.c_wchar(key))
                if scan == -1:
                    raise UnsupportedUi(
                        f"character {key!r} has no virtual-key on the active "
                        "keyboard layout; use type_text for literal text",
                        details={"key": key},
                    )
                vk = scan & 0xFF
                needs_shift = bool(scan & 0x100)
                shift_added = needs_shift and MOD_SHIFT not in chord.modifiers
                if shift_added:
                    events.append(_key_input(MODIFIER_VK[MOD_SHIFT], up=False))
                events.append(_key_input(vk, up=False))
                events.append(_key_input(vk, up=True))
                if shift_added:
                    events.append(_key_input(MODIFIER_VK[MOD_SHIFT], up=True))
            else:  # pragma: no cover - .keyboard rejects these first
                raise UnsupportedUi(f"unmappable key {key!r}", details={"key": key})

            for vk in reversed(modifier_vks):
                events.append(_key_input(vk, up=True))
            _send_inputs(events)
            # Applications process accelerators on their message loop; a chord
            # sent with zero gap is frequently swallowed.
            time.sleep(0.02)

    def type_text(self, text: str) -> None:
        # KEYEVENTF_UNICODE bypasses the keyboard layout entirely, so text types
        # identically regardless of the operator's locale.
        batch: list[_INPUT] = []
        for char in text:
            if char == "\n":
                batch.append(_key_input(VK_MAP["enter"], up=False))
                batch.append(_key_input(VK_MAP["enter"], up=True))
                continue
            if char == "\t":
                batch.append(_key_input(VK_MAP["tab"], up=False))
                batch.append(_key_input(VK_MAP["tab"], up=True))
                continue
            if char == "\r":
                continue
            batch.append(_unicode_input(char, up=False))
            batch.append(_unicode_input(char, up=True))
            # SendInput has a per-call event ceiling; flush in chunks so long
            # text does not silently truncate.
            if len(batch) >= 200:
                _send_inputs(batch)
                batch = []
                time.sleep(0.005)
        _send_inputs(batch)

    def click_point(self, x: int, y: int, *, button: str = "left",
                    double: bool = False) -> None:
        width = user32.GetSystemMetrics(78) or user32.GetSystemMetrics(0)   # CXVIRTUALSCREEN
        height = user32.GetSystemMetrics(79) or user32.GetSystemMetrics(1)  # CYVIRTUALSCREEN
        left = user32.GetSystemMetrics(76)
        top = user32.GetSystemMetrics(77)
        if width <= 0 or height <= 0:
            raise BackendError("could not determine screen metrics for a click",
                               details={"x": x, "y": y})
        # MOUSEEVENTF_ABSOLUTE coordinates are normalised to 0..65535 across the
        # virtual desktop, which is what makes this correct on multi-monitor
        # setups where raw pixels would be off-screen.
        nx = int(round((x - left) * 65535 / max(1, width - 1)))
        ny = int(round((y - top) * 65535 / max(1, height - 1)))

        down, up = {
            "left": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
            "right": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
            "middle": (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
        }[button]

        def _mouse(flags: int) -> _INPUT:
            return _INPUT(type=INPUT_MOUSE,
                          union=_INPUTUNION(mi=_MOUSEINPUT(
                              dx=nx, dy=ny, mouseData=0,
                              dwFlags=flags | MOUSEEVENTF_ABSOLUTE,
                              time=0, dwExtraInfo=None)))

        _send_inputs([_mouse(MOUSEEVENTF_MOVE)])
        time.sleep(0.01)
        clicks = 2 if double else 1
        for _ in range(clicks):
            _send_inputs([_mouse(down), _mouse(up)])
            if double:
                time.sleep(0.03)

    # --- evidence -------------------------------------------------------

    def screenshot(self, *, window_handle: int | None = None,
                   path: str | None = None) -> str | None:
        if self._screenshot_backend != "pillow":
            return None
        try:
            from PIL import ImageGrab

            bbox = None
            if window_handle:
                rect = _window_rect(int(window_handle))
                if not rect.is_empty:
                    bbox = (rect.left, rect.top, rect.right, rect.bottom)
            image = ImageGrab.grab(bbox=bbox, all_screens=bbox is None)
            target = path or os.path.join(
                os.environ.get("TEMP", "."), f"pilot-{int(time.time()*1000)}.png")
            os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
            image.save(target, "PNG")
            return target
        except Exception:
            # Evidence capture must never break an action.
            return None

    def sleep(self, seconds: float) -> None:
        if seconds > 0:
            time.sleep(seconds)


__all__ = ["UiaWindowsBackend"]
