# Machine-dependent integration tests

These tests drive a **real Windows desktop**. They move the mouse, synthesise
keystrokes, take over foreground focus, and launch stock applications. Nothing
here is safe to run unattended on a machine someone is using.

They are therefore double-gated and skip by default:

1. the host must be Windows (`sys.platform == "win32"`), and
2. `KLEARFLOW_PILOT_WINDOWS_INTEGRATION=1` must be set.

## Running them

```powershell
# from the repository root, on Windows, in an interactive session
python -m pip install uiautomation
$env:KLEARFLOW_PILOT_WINDOWS_INTEGRATION = "1"
python -m pytest pilot/adapters/windows/tests/integration -v
```

## Requirements

* Windows 10 or 11 with an **interactive desktop session** — not an SSH shell,
  not a service account, not a locked screen. Synthetic input needs a real
  session station.
* `uiautomation` installed (`pip install uiautomation`).
* Notepad and Calculator present (both are stock, but can be removed on
  hardened images).
* The session must not be elevated relative to the target applications. A
  non-elevated process cannot send input to an elevated window (UIPI); the
  adapter surfaces that as `BACKEND_ERROR`.

## Why they cannot run in ordinary CI

Standard hosted CI runners have no interactive desktop, so `SendInput`
silently discards events and UIA returns empty trees. If you need these in CI,
use a self-hosted Windows runner configured with an autologon interactive
session.
