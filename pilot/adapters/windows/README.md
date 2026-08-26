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
| `control_selectors.py` | Tiered semantic resolution (AutomationId → exact role/name → structural) | yes |
| `guards.py` | Elevation, UAC, foreground-identity and unexpected-modal checks | yes |
| `expectations.py` | Post-condition verification for input operations | yes |
| `redaction.py` | Secret handling in evidence and error payloads | yes |
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

Resolution runs in **tiers**, strongest identification first:

1. `automation_id` — the developer-assigned stable handle
2. exact / case-insensitive `name` + `role`, optionally scoped by ancestry
3. relaxed name (`contains`, `startswith`, `regex`)
4. structural only (role / class / pattern, no identifying text)

The **first tier that matches anything decides the outcome.** If that tier
matched more than one element, that is an ambiguity to report — not a field to
break with a tie-breaker. `evidence.resolution.tier` records which tier fired,
so a mission log shows when identification was weak or fell back.

`require_unique` defaults to **true**: an ambiguous semantic match is rejected
rather than resolved by ranking. Acting on the highest-scoring of several
indistinguishable controls is how automation clicks the wrong button, so the
caller must opt *out* of safety, not into it. Use `within`, `automation_id`, or
an explicit `index` to disambiguate.

`min_tier: "automation_id"` forbids a silent fallback to name matching — useful
when an app's automation ids are contractual.

**Ancestry scoping** distinguishes "the Save button *in the Save As dialog*"
from "any Save button on the desktop":

```python
{"name": "Save", "role": "button",
 "within": {"name": "Save As", "role": "window"}}
```

Unknown selector keys are rejected, so a typo cannot silently widen a search.

When a selector misses, the error carries **near misses**: elements that
matched the name but failed another criterion, each with the reason
(`disabled`, `offscreen`, `role is 'text', wanted 'button'`). "Found it but it
was disabled" and "no such control" need different recovery, and a planner
cannot tell them apart otherwise.

## Hardening rules

These are enforced by the adapter, not left to callers. Each is pinned by a
test class in `tests/unit/test_hardening.py`.

### Input delivery is not completion

Every input operation reports two separate facts:

```python
evidence["input_dispatched"]     # the keystroke/click was delivered
evidence["completion_verified"]  # the intended end state was observed
```

Without a declared `expect`, the second is `false` and the Result says so —
nothing downstream can mistake "we pressed the key" for "the thing happened".
Declaring one makes completion checkable:

```python
{"operation": "send_keys", "arguments": {
    "keys": ["ctrl+s"],
    "expect": {"window_title": "Save As"}}}
```

`expect` accepts `selector` (+ `value`, `value_match`, `absent`),
`window_title`, and `window_absent`. It is polled until it holds or the
action's deadline expires. An unmet expectation fails the action with
`COMPLETION_UNVERIFIED`.

`set_text` is the exception: it reads the value back through ValuePattern, so
it verifies completion directly.

### Unexpected modals stop execution

A dialog the action did not declare means the application asked something the
mission never anticipated. Execution stops with `UNEXPECTED_MODAL` rather than
pushing more input at whatever is now in front. Declare an expected dialog via
`expect.window_title`, or set `allow_modals: true` as an explicit escape hatch.

### Foreground identity is checked around every input

Focus moving to a **different process** during an input event means the
keystrokes may have gone elsewhere: `FOREGROUND_CHANGED`, never retryable,
`side_effect_possible: true`. Focus moving between windows of the *same*
process is legitimate (an app opening its own dialog) and handled by the modal
guard instead.

### Elevation escalates; UAC is never driven

The target's Windows integrity level is compared to this process's **before**
any input is dispatched. A higher-integrity target yields `ELEVATION_REQUIRED`
with a remedy naming a human action — no workaround is attempted. A target
whose integrity cannot be read is recorded as suspicious, not assumed equal.

A detected UAC consent prompt yields `UAC_PROMPT_DETECTED` and stops. This
adapter has no code path that accepts or dismisses consent UI.

### Coordinate fallbacks re-read geometry

`click_control` re-reads the element's bounding rectangle immediately before
clicking rather than reusing the rect from discovery. A window that moved,
resized, or changed monitor between the two is clicked where it *now* is.
`geometry_tolerance_px` makes excessive drift fatal (`STALE_ELEMENT`) instead.

### Re-discovery before every attempt

`_find_element` re-walks the control tree on every polling attempt. Nothing is
carried over from a previous attempt, so the adapter never acts on an element
that has since moved or been destroyed.

### Non-idempotent actions do not blindly retry

`Result.retryable` is the conjunction of two independent facts:

* is the failure transient, **and**
* is repeating safe — nothing dispatched, or the operation is idempotent?

`error.retry_reasoning` spells out the decision. `type_text`, `send_keys`,
`invoke_control`, `toggle_control`, `click_*`, and `launch_application` are
marked non-idempotent; a failure after their input was dispatched reports
`retryable: false` with `side_effect_possible: true`.

**That combination means the outcome is unknown, not failed.** Re-discover
state and decide explicitly; do not repeat.

### Evidence may contain secrets

Control values from password-like controls (by name, automation id, or
`PasswordBox` class) and credential-shaped values anywhere (JWTs, provider key
prefixes, PEM blocks, URLs with inline credentials) are replaced with
`<redacted:sensitive>` in evidence and error payloads, including echoed
arguments. Tree summaries carry no values at all.

Screenshots cannot be redacted after capture, so they are **labelled** rather
than sanitised: every capture carries `contains_untrusted_pixels: true` and a
sensitivity note for downstream retention policy. Capture stays opt-in per
adapter (`capture_screenshots=False` by default).

### Never a process kill

No operation, and no backend method, kills or terminates a process.
`close_window` uses the accessible Close affordance or `alt+f4`. A window that
will not close is reported as still present — hanging is a fact to report, not
a reason to destroy unsaved work.

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
| `COMPLETION_UNVERIFIED` | no | Input dispatched, declared post-condition never held |
| `UNEXPECTED_MODAL` | no | An undeclared dialog appeared; execution stopped |
| `FOREGROUND_CHANGED` | no | Focus moved to another process during input |
| `ELEVATION_REQUIRED` | no | Target runs at a higher integrity level |
| `UAC_PROMPT_DETECTED` | no | Consent prompt on screen; adapter will not drive it |
| `STALE_ELEMENT` | **yes** | Element moved or vanished between discovery and use |
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

## Validation status

`WINDOWS_VALIDATION_MATRIX.md` tracks 14 scenarios against real Windows.
**No row is marked PASS**: this lane was developed on Linux, so every line of
`uia_backend.py` is unexecuted. Read it before trusting any Windows behaviour.

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
* **Focus theft inside a single call.** The foreground guard brackets each
  input call, so a steal that occurs and reverts *within* one `SendInput` is
  invisible to it. Catching that needs a foreground event hook, which this
  lane does not install.
* **UAC detection is a backstop.** Real consent prompts run on a separate
  secure desktop and are usually not in this session's window list at all. The
  primary defence is the absence of any code path that drives consent UI.
* **File Explorer is unvalidated.** See `WINDOWS_VALIDATION_MATRIX.md` row 3;
  treat it as unsupported until that row is executed.
* **No vision fallback yet.** Custom-rendered UI (some Electron, games,
  canvas-based apps) exposes no usable patterns. The adapter detects and
  reports this rather than flailing.
