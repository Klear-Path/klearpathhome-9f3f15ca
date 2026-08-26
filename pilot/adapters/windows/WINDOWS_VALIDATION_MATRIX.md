# Windows Validation Matrix — KlearFlow Pilot Windows Operator

Scope: the `uiautomation`-backed adapter at `pilot/adapters/windows/`.

## How to read the status column

| Status | Meaning |
|---|---|
| **SIM** | Logic verified against the in-memory simulated backend. Proves the adapter's *decision-making* — selector tiering, guard firing, error classification, retry gating. Proves nothing about UIA, COM, or `SendInput`. |
| **UNPROVEN** | Written and reviewed, never executed against Windows. No claim is made. |
| **BLOCKED** | Cannot be validated from this environment at all, and needs a human on a real desktop. |

**No row in this matrix is marked PASS.** Every line of Windows-specific code
(`uia_backend.py`) remains unexecuted: this lane was developed on Linux, where
`sys.platform != "win32"` makes that module unimportable by design. SIM is a
statement about the platform-free layers only.

Run the machine-dependent suite before trusting any row:

```powershell
python -m pip install uiautomation Pillow pytest
$env:KLEARFLOW_PILOT_WINDOWS_INTEGRATION = "1"
python -m pytest pilot/adapters/windows/tests/integration -v
```

---

## 1. Notepad

| | |
|---|---|
| **Status** | SIM (mission logic) / UNPROVEN (Windows) |
| **Automated by** | `tests/unit/test_missions.py::TestNotepadProof*` (SIM), `tests/integration/test_windows_desktop.py::TestNotepadProofMission` (UNPROVEN) |

**Procedure.** Launch `notepad.exe`; resolve the editor by role `document` +
Value pattern; `set_text` "KlearFlow Pilot"; `ctrl+s` declaring
`expect.window_title="Save As"`; fill the filename field; invoke Save declaring
`expect.window_absent="Save As"`; close; read the file with a plain `open()`
outside the adapter and compare bytes.

**Expected.** File contains exactly `KlearFlow Pilot`. Mission fails loudly on
any mismatch.

**Windows-specific risk.** The editor control class changed from `Edit` to
`RichEditD2DPT` in the Windows 11 rewrite, and the modern Notepad is a Store
app with tabs — a second tab changes the tree shape. The selector targets
role + Value pattern rather than a class name specifically to survive this,
but that has not been confirmed against either build.

---

## 2. Calculator

| | |
|---|---|
| **Status** | SIM (mission logic) / UNPROVEN (Windows) |
| **Automated by** | `tests/unit/test_missions.py::TestCalculatorProof` (SIM), `tests/integration/...::TestCalculatorProofMission` (UNPROVEN) |

**Procedure.** Launch `calc.exe`; enumerate the control tree; invoke
`num7Button`, `plusButton`, `num8Button`, `equalButton` by automation id;
read `CalculatorResults` and assert `15`.

**Expected.** Display reads 15. Zero coordinate clicks (asserted:
`backend.clicks == []`).

**Windows-specific risk.** Calculator is a packaged app launched through a
stub, so the window belongs to `ApplicationFrameHost.exe` rather than the pid
`Popen` returned. `launch()` has a name-matching fallback for exactly this,
which is the single most likely thing in this matrix to be wrong in practice.
The result element sometimes reports its number only through the accessible
name ("Display is 15"); the mission handles both, untested.

---

## 3. File Explorer

| | |
|---|---|
| **Status** | UNPROVEN — no automated coverage |
| **Automated by** | *nothing* |

**Procedure.** Launch `explorer.exe`; enumerate; resolve the address bar
(`Breadcrumb Parent`) and the items view (`UIItemsView`); select an item by
name scoped `within` the items view.

**Expected.** Enumeration returns a tree with a `list`/`data_grid` items view;
selection changes the selected item.

**Why this is the weakest row.** Explorer is the hardest of the four targets
and has the least coverage. Specific hazards, none tested:

* `explorer.exe` frequently **returns immediately** and hands the request to
  the already-running shell process, so the launched pid has no window and the
  name-match fallback finds a pre-existing window instead of the new one.
* The desktop itself is an Explorer window (`Progman`/`WorkerW`), so a
  process-name match can resolve to the desktop rather than a browser window.
* The items view is virtualised: off-screen items are absent from the tree
  entirely, so a selector for an item below the fold legitimately finds
  nothing. The adapter reports `ELEMENT_NOT_FOUND`, which is technically true
  and practically misleading.

**Recommendation:** treat Explorer as unsupported until this row is executed.

---

## 4. Common Save As dialog

| | |
|---|---|
| **Status** | SIM (dialog flow, modal guard) / UNPROVEN (Windows) |
| **Automated by** | `test_missions.py` (flow), `test_hardening.py::TestUnexpectedModal` (guard) |

**Procedure.** As row 1. The dialog is resolved by title; the filename field by
role `edit` + Value pattern; the Save button by name scoped `within` the
dialog window.

**Expected.** Filename set, Save invoked, dialog closes. If an overwrite
confirmation appears it is an undeclared modal and the mission **stops**
rather than proceeding (`UNEXPECTED_MODAL`) — verified in SIM.

**Windows-specific risk.** The modern common dialog is `IFileDialog`, not the
classic `#32770`; automation id `1001` for the filename field is the classic
value and may not hold. The filename field is a ComboBox on some builds, which
the role-`edit` selector would miss. Scoping by ancestry is what stops the
Save button resolving to the parent app's own toolbar — untested on Windows.

---

## 5. Focus theft

| | |
|---|---|
| **Status** | SIM (guard logic) / UNPROVEN (Windows) |
| **Automated by** | `test_hardening.py::TestForegroundIdentity` (5 tests) |

**Procedure.** Begin an input operation on target A; have process B steal
foreground mid-operation; observe.

**Expected.** `FOREGROUND_CHANGED`, `retryable=false`,
`side_effect_possible=true`, both process names in the message. Focus moving
between windows *of the same process* is not theft (Notepad opening Save As)
— asserted separately.

**Windows-specific risk.** The guard compares foreground **before and after**
the input call, so a steal that occurs and reverts *inside* a single
`SendInput` is invisible to it. Narrowing that further needs a foreground
event hook, which this lane does not install.

---

## 6. Two matching controls

| | |
|---|---|
| **Status** | SIM / UNPROVEN (Windows) |
| **Automated by** | `test_hardening.py::TestAmbiguityRejection` (6 tests), `TestScopedAncestry` (6 tests) |

**Procedure.** Present two controls with identical name and role; resolve
without disambiguation, then with `within` scoping, then with `index`.

**Expected.** Unscoped → `AMBIGUOUS_SELECTOR`, `retryable=false`, both
candidates listed, hint naming `within`/`automation_id`/`index`. Scoped →
resolves. Explicit `index` → resolves with a "ranking bypassed" warning.

**This is a behaviour change from Round 1**, where the higher-scoring match won
silently and depth was the tiebreaker. Depth is not a semantic difference and
must not decide which button gets pressed.

---

## 7. Elevated target

| | |
|---|---|
| **Status** | SIM (policy) / **BLOCKED** (Windows) |
| **Automated by** | `test_hardening.py::TestElevationAndUac` (9 tests) |

**Procedure.** Run Pilot at medium integrity; target a high-integrity window
(e.g. an elevated Registry Editor); attempt any interaction.

**Expected.** `ELEVATION_REQUIRED` **before any input is dispatched**, not a
downstream `SendInput` failure. Remedy names a human action ("restart the
operator at a matching integrity level"). Never retryable. No elevation
attempted, ever.

**Why BLOCKED.** Needs two processes at different integrity levels on a real
desktop with a human to approve the elevation. The token-reading path
(`OpenProcessToken` → `GetTokenInformation(TokenIntegrityLevel)` → SID
sub-authority) is entirely unexecuted, and it is intricate ctypes code —
treat it as the second-most-likely thing in this matrix to be wrong.

Note the asymmetry: when the target's integrity **cannot be read**, that is
recorded as suspicious rather than passed as equal, because failing to open a
token is itself a symptom of the boundary.

---

## 8. UAC prompt

| | |
|---|---|
| **Status** | SIM (policy) / **BLOCKED** (Windows) |
| **Automated by** | `test_hardening.py::TestElevationAndUac` |

**Expected.** `UAC_PROMPT_DETECTED`, execution stops, **no input dispatched**
(asserted). The adapter never clicks Yes and never dismisses the prompt.

**Windows-specific reality.** Real UAC runs on a separate secure desktop, so
the consent window is normally not in this session's window list at all —
detection by process name (`consent.exe`, `CredentialUIBroker.exe`) works only
when secure-desktop prompting is disabled by policy. The guard is therefore a
backstop, not a primary defence. The primary defence is that this adapter has
no code path that drives consent UI.

---

## 9. DPI 100%

| | |
|---|---|
| **Status** | UNPROVEN |
| **Automated by** | *nothing DPI-specific* |

**Procedure.** Single display at 100%; run rows 1 and 2; run a `click_control`
and confirm the click lands on the intended control.

**Expected.** Coordinates match physical pixels; clicks land correctly.

**Note.** This is the baseline case and the one most likely to work. It is
still UNPROVEN because no click has been executed on Windows at all.

---

## 10. DPI 150%

| | |
|---|---|
| **Status** | UNPROVEN |
| **Automated by** | Geometry-freshness logic only (`TestFreshGeometry`) |

**Procedure.** Set the display to 150%; **log out and back in** (per-monitor
awareness is set at process start); repeat row 9.

**Expected.** Clicks land correctly; `evidence.guards.geometry` shows the rect
re-read at click time.

**Windows-specific risk.** The adapter calls
`SetProcessDpiAwarenessContext(PER_MONITOR_AWARE_V2)` at backend construction
and falls back through `SetProcessDpiAwareness` → `SetProcessDPIAware`. If a
host embeds this lane in a process that already set an awareness context, the
call fails silently and every coordinate is virtualised — clicks land at
roughly ⅔ offset at 150%. `capabilities().notes` reports which mode was
actually achieved; **check it before trusting any coordinate click.**

---

## 11. Second monitor

| | |
|---|---|
| **Status** | UNPROVEN |
| **Automated by** | `TestFreshGeometry::test_a_moved_window_is_clicked_at_its_new_position` (simulates a 1920px drift) |

**Procedure.** Two monitors, ideally at different scale factors; move the
target window to the secondary; run row 9; then move the window *between*
resolution and click.

**Expected.** Clicks land correctly on the secondary monitor, including at
negative coordinates when it is positioned left of or above the primary.

**Windows-specific risk.** `click_point` normalises to the virtual desktop via
`SM_XVIRTUALSCREEN`/`SM_CXVIRTUALSCREEN` (76/78) rather than the primary
display, which is the correct approach for negative-origin layouts — but the
arithmetic is unverified. Mixed per-monitor DPI is the hardest sub-case and
the most likely to be wrong.

The Round 2 fix that matters here: geometry is re-read immediately before the
click rather than reused from discovery, so a window that moved between the
two is clicked where it now is. Verified in SIM, unproven on Windows.

---

## 12. Slow launch

| | |
|---|---|
| **Status** | SIM (partial) / UNPROVEN (Windows) |
| **Automated by** | `TestRediscoverBeforeRetry::test_an_element_appearing_late_is_picked_up` |

**Procedure.** Launch a cold-start application (first-run Office, a packaged
app after reboot); observe waiting behaviour.

**Expected.** `launch_application` polls to `wait_for_window_seconds`;
`wait_for_element` re-walks the tree each attempt; a late-appearing control is
found. `LAUNCH_FAILED` is retryable.

**Windows-specific risk.** A splash screen can satisfy the "a window appeared"
condition while the real UI is still loading, so the adapter proceeds against
the wrong window. There is no "window is ready" heuristic beyond existence.
Declaring `expect` on the first post-launch action is the mitigation, and the
proof missions do this; nothing enforces it.

---

## 13. Interrupted mission / resume

| | |
|---|---|
| **Status** | **BLOCKED — architecturally out of scope for this lane** |
| **Automated by** | Partial-state reporting only |

The adapter is stateless by design and owns no mission state, so it cannot
resume anything: resumption belongs to the core runtime's mission controller.
What this lane owes the controller is enough information to resume *safely*,
and that is what Round 2 added:

* `error.side_effect_possible` — whether the action may already have applied.
* `evidence.idempotent` — whether repeating is safe.
* `error.retry_reasoning` — the conjunction of both, in words.
* `state_before` / `state_after` on every Result, including on failure.

**What the integrator must know:** a Result with `retryable=false` and
`side_effect_possible=true` means *the outcome is unknown, not failed*. A
resume that re-runs such an action duplicates it. The controller must
re-discover state and decide, which is precisely the Manus rule this encodes.

**Untested:** whether that information is sufficient for a real resume. Nobody
has built the controller against it yet.

---

## 14. Inaccessible / custom control

| | |
|---|---|
| **Status** | SIM / UNPROVEN (Windows) |
| **Automated by** | `test_operations.py::TestInvoke::test_pattern_less_control_is_unsupported_ui`, `TestControlTree::test_flags_an_inaccessible_window`, `TestCalculatorProof::test_fails_when_the_ui_is_entirely_inaccessible` |

**Procedure.** Target a custom-rendered surface (a canvas app, a game, some
Electron windows) exposing no UIA patterns.

**Expected.** `UNSUPPORTED_UI`, `retryable=false`, `advertised_patterns: []`,
and a `fallback` hint naming the vision escalation. A window whose whole tree
is one opaque node gets `accessibility_warning` on `get_control_tree`.

**Deliberate non-behaviour.** The adapter does **not** silently fall back to
coordinate clicking when patterns are absent. `click_control` is available but
must be requested; automatic degradation would hide the accessibility gap that
the vision backend is meant to fill.

---

## Summary

| # | Scenario | Status |
|---|---|---|
| 1 | Notepad | SIM / UNPROVEN |
| 2 | Calculator | SIM / UNPROVEN |
| 3 | File Explorer | **UNPROVEN, no coverage** |
| 4 | Save As dialog | SIM / UNPROVEN |
| 5 | Focus theft | SIM / UNPROVEN |
| 6 | Two matching controls | SIM / UNPROVEN |
| 7 | Elevated target | SIM / **BLOCKED** |
| 8 | UAC prompt | SIM / **BLOCKED** |
| 9 | DPI 100% | UNPROVEN |
| 10 | DPI 150% | UNPROVEN |
| 11 | Second monitor | UNPROVEN |
| 12 | Slow launch | SIM partial / UNPROVEN |
| 13 | Interrupted mission | **BLOCKED — out of lane** |
| 14 | Inaccessible control | SIM / UNPROVEN |

**Nothing here is PASS.** Highest-risk rows, in order: **7** (unexecuted
token ctypes), **3** (no coverage at all, hardest target), **10/11**
(coordinate arithmetic + DPI awareness), **2** (packaged-app launch
fallback).

## Port note (pywinauto)

Rows 1–14 are library-agnostic: they describe adapter *behaviour*, not
`uiautomation` behaviour. Everything above `uia_backend.py` — tiering, guards,
expectations, redaction, retry gating — is unchanged by a backend swap, so
this matrix is the acceptance criteria for a pywinauto port too. A port
replaces one file and must satisfy the same rows.
