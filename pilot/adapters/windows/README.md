# KlearFlow Pilot — Windows Operator Adapter

Native Windows computer-control lane. Turns a Pilot `Action` into desktop work
(launch, focus, inspect, click, type, save) and returns a Pilot `Result`
describing what happened, with before/after state and evidence.

This is an **adapter only**. It owns no mission state, plans nothing, and never
retries on its own — it reports `retryable` and lets the mission controller
decide.

## Execution preference

The lane brief's ordering is encoded in the design, not left to convention:

1. **UI Automation / accessibility patterns** — `invoke_control`, `set_text`,
   `toggle_control`, `select_item`, `expand_control`. Always tried first.
2. **Deterministic keyboard/mouse** — `send_keys`, `type_text`. Used for
   accelerators (`ctrl+s`) and for controls with no Value pattern.
3. **Coordinate interaction** — `click_control` (element located semantically,
   only the final press uses pixels) and `click_point` (raw coordinates). Both
   tag themselves in `evidence.fallback_used`, so a mission log shows exactly
   where the adapter had to drop down a level.

## Quick start

```python
from pilot.adapters.windows import WindowsOperatorAdapter, Action

adapter = WindowsOperatorAdapter()          # auto-selects a backend
print(adapter.describe())                   # capabilities + operation catalogue

result = adapter.execute(Action(
    operation="launch_application",
    arguments={"command": "notepad.exe"},
))
print(result.success, result.stdout)
```

`execute()` never raises. Every failure — unknown operation, missing control,
inaccessible UI, a COM explosion — comes back as a `Result` with
`success=False` and a structured `error`.

## Module map

| Module | Responsibility | Platform-free? |
|---|---|---|
| `contracts.py` | `Action` / `Result`, and `coerce_action` — the seam for the core runtime's own types | yes |
| `errors.py` | Failure taxonomy with stable `code` and `retryable` | yes |
| `model.py` | `ElementSnapshot`, `WindowInfo`, `Rect`, role normalisation | yes |
| `control_selectors.py` | Semantic matching and ranking | yes |
| `keyboard.py` | Chord parsing (`"ctrl+shift+s"` → `Chord`) | yes |
| `backend.py` | `UiaBackend` protocol + `BackendCapabilities` + `NullBackend` | yes |
| `operations.py` | Operation registry and handlers | yes |
| `safety.py` | Confirmation gate for risky actions | yes |
| `evidence.py` | Before/after state and screenshot capture | yes |
| `adapter.py` | `execute()` envelope | yes |
| `uia_backend.py` | **The only Windows-specific module** | no |
| `fakes.py` | In-memory backend + simulated Notepad/Calculator | yes |
| `missions/` | The two scripted proof missions | yes |

Everything except `uia_backend.py` talks to the `UiaBackend` protocol, never to
Windows. That is what lets the whole lane be tested off-Windows, and it is the
same seam a vision backend will plug into.

> **Note:** the selector module is `control_selectors.py`, not `selectors.py`.
> A module named `selectors` shadows the standard library module that `socket`
> imports, which breaks any process that puts this directory on `sys.path`.

## Operations

| Operation | Goal | Notes |
|---|---|---|
| `list_windows` | 1 | Top-level windows; filters untitled helper windows by default |
| `get_foreground_window` | 2 | Absence of focus is reported as success, not an error |
| `launch_application` | 3 | `shell=False`; no metacharacter interpretation |
| `focus_window` | 4 | **Verifies** focus actually moved; failure is reported, not assumed |
| `get_control_tree` | 5 | Bounded walk; flags windows with no interactable children |
| `find_controls` | 6 | Scored matches; zero matches is a successful empty answer |
| `invoke_control` | 7 | Picks Invoke / SelectionItem / Toggle / Expand by element semantics |
| `set_text` | 8 | ValuePattern, self-verifying by default |
| `send_keys`, `type_text` | 9 | Chords vs. literal Unicode text |
| `click_control`, `click_point` | 10 | Semantic-then-pixel, and raw pixel |
| `screenshot` | 11 | Optional; degrades cleanly when Pillow is absent |
| `toggle_control`, `expand_control`, `select_item`, `get_element_state`, `wait_for_element`, `close_window`, `capabilities` | — | Supporting verbs |

`close_window` uses the accessible Close affordance or `alt+f4`. It is never a
process kill: killing a process loses unsaved work.

## Selectors

Controls are addressed by meaning, never position:

```python
{"automation_id": "num7Button", "role": "button"}       # most stable
{"name": "Save", "role": "button", "name_match": "iequals"}
{"role": "document", "requires_patterns": ["value"]}     # by capability
```

`name_match` / `value_match` accept `exact`, `iequals`, `contains`,
`startswith`, `regex`. Matches are **scored** — automation id outranks name,
exact name outranks a substring, shallower elements break ties — and ordering
is deterministic for a given tree. Pass `require_unique: true` to make a
genuine tie an `AMBIGUOUS_SELECTOR` failure rather than a guess.

Unknown selector keys are rejected, so a typo cannot silently widen a search.

When a selector misses, the error carries **near misses**: elements that
matched the name but failed another criterion, each with the reason
(`disabled`, `offscreen`, `role is 'text', wanted 'button'`). "Found it but it
was disabled" and "no such control" need different recovery, and a planner
cannot tell them apart otherwise.

## Error codes

| Code | Retryable | Meaning |
|---|---|---|
| `UNSUPPORTED_OPERATION` | no | Unknown verb, or backend lacks a facility |
| `INVALID_ARGUMENTS` | no | Missing/malformed arguments |
| `PLATFORM_UNAVAILABLE` | no | Not Windows, or UIA stack missing |
| `SAFETY_REFUSAL` | no | Confirmation gate declined |
| `WINDOW_NOT_FOUND` | **yes** | No matching top-level window |
| `ELEMENT_NOT_FOUND` | **yes** | Selector missed within the timeout |
| `AMBIGUOUS_SELECTOR` | no | Tie; the selector must change |
| `ELEMENT_NOT_INTERACTABLE` | **yes** | Disabled, offscreen, or focus refused |
| `UNSUPPORTED_UI` | no | No accessible pattern — the vision hand-off point |
| `LAUNCH_FAILED` | **yes** | Program did not start or produced no window |
| `TIMEOUT` | **yes** | Exceeded `Action.timeout_seconds` |
| `BACKEND_ERROR` | **yes** | Unclassified COM/UIA fault |
| `VERIFICATION_FAILED` | no | Action ran, observed end state was wrong |
| `INTERNAL_ERROR` | no | Unexpected fault, still returned as a `Result` |

## Safety

`safety.py` is **additive** — it can only withhold permission, never grant it,
and it disables nothing that already exists in KlearForge.

* Read-only operations always pass.
* High-risk actions are refused unless the adapter was constructed with
  `allow_high_risk=True` (default: off).
* Payloads matching destructive patterns (`format `, `vssadmin delete`,
  `Remove-Item -Recurse`, …) are escalated to high risk **regardless of the
  declared level**, because a planner that labels `format c:` as low risk is
  exactly the case worth catching.
* An unrecognised risk label is treated as `HIGH`, not as permissive.
* The gate runs before any backend call, so a refusal has no side effect.

No credential handling of any kind is present, and none should be added here.

## Swapping in the canonical contract

`coerce_action` accepts an `Action`, a mapping, or any object with the same
field names. The core runtime can pass its own type unchanged:

```python
result = adapter.execute(core_runtime_action)   # duck-typed, no import needed
payload = result.to_dict()                      # plain JSON-safe dict
```

To adopt the canonical dataclasses outright, replace `contracts.py` — it is the
only module that defines them, and everything else imports from it.

## Adding a vision fallback

Implement the `UiaBackend` protocol and set `vision=True` in
`BackendCapabilities`. No other module changes:

* `adapter._assert_backend_supports` gates on declared capabilities, so a
  vision backend advertises what it can do rather than failing by exception.
* `UNSUPPORTED_UI` errors already carry `advertised_patterns` and a `fallback`
  hint, so the escalation point is machine-readable.
* `get_control_tree` sets `accessibility_warning` on windows with no
  interactable children — the signal that UIA alone will not be enough.
* A composing backend that tries UIA first and falls back to vision per-call is
  a drop-in, because every method takes and returns platform-free types.

## Testing

```bash
# Unit suite — any platform, no desktop, no Windows dependencies
python -m pytest pilot/adapters/windows/tests/unit -v

# Everything (integration auto-skips off Windows)
python -m pytest pilot/adapters/windows/tests -v

# Integration — Windows only, interactive desktop, opt-in
#   PowerShell:
$env:KLEARFLOW_PILOT_WINDOWS_INTEGRATION = "1"
python -m pytest pilot/adapters/windows/tests/integration -v
```

The unit suite runs against `fakes.py`: an in-memory backend plus simulated
Notepad and Calculator that mirror the real applications' **control contract**
(automation ids, control types, accessible patterns, the Save-As dialog flow).
It exercises selector resolution, action ordering, verification, evidence, and
every error path — and the Notepad proof performs a **real filesystem write**
that is read back independently, so the on-disk assertion is genuine.

It does **not** exercise UIA, COM, or `SendInput`. Only
`tests/integration/` does, and only on a real Windows desktop. See
`tests/integration/README.md`.

Time is virtual in the unit suite (`FakeBackend.sleep` advances an internal
clock), so timeout and polling behaviour is tested without wall-clock delay.

## Proof missions

```python
from pilot.adapters.windows import WindowsOperatorAdapter
from pilot.adapters.windows.missions import notepad_proof, calculator_proof

report = notepad_proof.run(WindowsOperatorAdapter())
print(report.summary())
assert report.verified
```

**Notepad** — launch, locate the editor semantically, type `KlearFlow Pilot`,
save via `ctrl+s` + the Save As dialog, close, then read the file back with a
plain `open()` **outside the adapter** and compare bytes. Verifying a write by
asking the component that performed it to read it back proves very little; the
point is an independent observer. Six negative tests confirm the proof fails on
wrong text, truncation, a one-character difference, extra content, an empty
file, a wrong encoding, and a file that was never written.

**Calculator** — launch, enumerate the control tree, compute 7 + 8 by invoking
buttons via their automation ids (no coordinates anywhere), and verify the
display reads `15`. A test asserts `backend.clicks == []` to keep the
no-coordinates property honest.

## Dependencies

| Package | Required for | Why |
|---|---|---|
| `uiautomation>=2.0.18` | Driving a real desktop | Wraps `IUIAutomation` via comtypes. Preferred over pywinauto (which layers a second control abstraction over UIA) and over hand-rolled comtypes (substantial type-library boilerplate). |
| `Pillow>=10.0.0` | Screenshots (optional) | Absence degrades to `screenshots=False`, not a crash. |
| `pytest>=7.4` | Tests | — |

Importing the package, running the unit suite, and calling `describe()` need
**none** of these — only the standard library.

Keyboard and mouse input use `SendInput` through `ctypes` directly rather than
the `uiautomation` package's own `SendKeys` string DSL, so chord handling stays
in `keyboard.py` where it is unit-tested.

## Known limitations

* **Elevation (UIPI).** A non-elevated process cannot send input to, or fully
  inspect, an elevated window. Surfaces as `BACKEND_ERROR` from `SendInput`.
  Run the operator at the same integrity level as its targets.
* **Foreground lock.** Windows can refuse `SetForegroundWindow`. The adapter
  uses the documented `AttachThreadInput` workaround and then **verifies**,
  reporting `ELEMENT_NOT_INTERACTABLE` (retryable) if focus did not move.
* **Timeouts are cooperative.** `Action.timeout_seconds` is checked between
  polling attempts. A single blocking COM call cannot be preempted from here.
* **Interactive session required.** Synthetic input needs a real session
  station. Over SSH, as a service, or on a locked screen, `SendInput` silently
  discards events and UIA returns empty trees.
* **Bounded tree walks.** `control_tree` caps depth (12) and elements (2000).
  Very large applications will truncate; `stats` reports the totals seen.
* **No thread safety.** UIA COM objects are apartment-bound. Construct one
  backend per worker thread.
* **Element cache invalidation.** Snapshots hold opaque `runtime_id`s resolved
  through a bounded cache. If the UI changes between capture and interaction,
  the backend re-walks once, then reports `ELEMENT_NOT_FOUND`.
* **Localisation.** Name-based selectors are locale-sensitive. Prefer
  `automation_id`; the proof missions do.
* **No vision fallback yet.** Custom-rendered UI (some Electron, games,
  canvas-based apps) exposes no usable patterns. The adapter detects and
  reports this rather than flailing.
