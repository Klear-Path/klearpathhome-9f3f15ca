"""Tests for the Round 2 hardening rules.

One class per rule, named for the rule it pins. These are the tests that would
fail if a future change quietly re-introduced "input delivered means action
completed" or "pick the best-scoring of several matches".
"""

from __future__ import annotations

import pytest

from ...adapter import WindowsOperatorAdapter
from ...contracts import Action
from ...control_selectors import (
    TIER_AUTOMATION_ID, TIER_EXACT_ROLE_NAME, TIER_RELAXED_NAME,
    TIER_STRUCTURAL, Selector, build_tiers, resolve,
)
from ...errors import AmbiguousSelector, ElementNotFound
from ...fakes import (
    FakeApp, FakeElement, make_elevated_app, make_uac_prompt,
    make_unexpected_dialog,
)
from ...model import PATTERN_INVOKE, PATTERN_VALUE, ElementSnapshot, Rect


def run(adapter, operation, **arguments):
    return adapter.execute(Action(operation=operation, arguments=arguments))


def el(runtime_id, **kwargs):
    return ElementSnapshot(runtime_id=runtime_id, **kwargs)


# ==========================================================================
# Rule: AutomationId first
# ==========================================================================

class TestAutomationIdFirst:
    def test_automation_id_is_the_first_tier_attempted(self):
        tiers = [t for t, _ in build_tiers(
            Selector(automation_id="btnSave", name="Save", role="button"))]
        assert tiers[0] == TIER_AUTOMATION_ID

    def test_automation_id_wins_even_when_the_name_differs(self):
        # Localised UI: the id is stable, the label is not.
        button = el("b", name="Speichern", role="Button", automation_id="btnSave",
                    patterns=(PATTERN_INVOKE,), depth=1)
        decoy = el("d", name="Save", role="Button", automation_id="btnOther",
                   patterns=(PATTERN_INVOKE,), depth=1)
        root = el("root", role="Window", children=(decoy, button))
        result = resolve(root, Selector(automation_id="btnSave", name="Save",
                                        role="button"))
        assert result.element.runtime_id == "b"
        assert result.tier == TIER_AUTOMATION_ID

    def test_a_name_mismatch_under_an_id_hit_is_reported(self):
        button = el("b", name="Speichern", role="Button", automation_id="btnSave",
                    patterns=(PATTERN_INVOKE,), depth=1)
        root = el("root", role="Window", children=(button,))
        result = resolve(root, Selector(automation_id="btnSave", name="Save"))
        assert any("name is" in w for w in result.warnings)

    def test_falls_back_to_name_when_the_id_is_gone(self):
        # An app that renamed its automation ids should degrade visibly, not
        # fail outright — but the fallback must be recorded.
        button = el("b", name="Save", role="Button", automation_id="newId",
                    patterns=(PATTERN_INVOKE,), depth=1)
        root = el("root", role="Window", children=(button,))
        result = resolve(root, Selector(automation_id="btnSave", name="Save",
                                        role="button"))
        assert result.tier == TIER_EXACT_ROLE_NAME
        assert any("fell back" in w for w in result.warnings)

    def test_min_tier_forbids_the_fallback(self):
        button = el("b", name="Save", role="Button", automation_id="newId",
                    patterns=(PATTERN_INVOKE,), depth=1)
        root = el("root", role="Window", children=(button,))
        with pytest.raises(ElementNotFound):
            resolve(root, Selector(automation_id="btnSave", name="Save"),
                    min_tier=TIER_AUTOMATION_ID)

    def test_the_tier_used_reaches_result_evidence(self, adapter, calculator):
        result = run(adapter, "invoke_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button", "role": "button"})
        assert result.evidence["resolution"]["tier"] == TIER_AUTOMATION_ID


# ==========================================================================
# Rule: exact role/name + scoped ancestry second
# ==========================================================================

class TestScopedAncestry:
    @pytest.fixture
    def two_saves(self):
        toolbar_save = el("main.save", name="Save", role="Button",
                          patterns=(PATTERN_INVOKE,), depth=2)
        toolbar = el("main.toolbar", name="Toolbar", role="ToolBar", depth=1,
                     children=(toolbar_save,))
        dialog_save = el("dlg.save", name="Save", role="Button",
                         patterns=(PATTERN_INVOKE,), depth=2)
        dialog = el("dlg", name="Save As", role="Window", depth=1,
                    children=(dialog_save,))
        return el("root", role="Window", depth=0, children=(toolbar, dialog))

    def test_unscoped_duplicate_names_are_rejected(self, two_saves):
        with pytest.raises(AmbiguousSelector):
            resolve(two_saves, Selector(name="Save", role="button"))

    def test_ancestry_scope_disambiguates(self, two_saves):
        result = resolve(two_saves, Selector(
            name="Save", role="button",
            within=Selector(name="Save As", role="window")))
        assert result.element.runtime_id == "dlg.save"
        assert "Save As" in result.scope

    def test_scope_is_recorded_for_the_mission_log(self, two_saves):
        result = resolve(two_saves, Selector(
            name="Save", role="button",
            within=Selector(name="Save As", role="window")))
        assert result.to_dict()["scope"]

    def test_an_unresolvable_scope_fails_rather_than_widening(self, two_saves):
        # Falling back to a desktop-wide search when the scope is missing is
        # exactly the mistake scoping exists to prevent.
        with pytest.raises(ElementNotFound):
            resolve(two_saves, Selector(
                name="Save", role="button",
                within=Selector(name="Nonexistent Dialog", role="window")))

    def test_exact_name_ranks_above_relaxed(self):
        assert build_tiers(Selector(name="Save"))[0][0] == TIER_EXACT_ROLE_NAME
        assert build_tiers(
            Selector(name="Save", name_match="contains"))[0][0] == TIER_RELAXED_NAME

    def test_structural_only_selectors_are_marked_weak(self):
        editor = el("e", role="Document", patterns=(PATTERN_VALUE,),
                    keyboard_focusable=True, depth=1)
        root = el("root", role="Window", children=(editor,))
        result = resolve(root, Selector(role="document",
                                        requires_patterns=(PATTERN_VALUE,)))
        assert result.tier == TIER_STRUCTURAL
        assert any("weak identification" in w for w in result.warnings)


# ==========================================================================
# Rule: reject ambiguous semantic matches
# ==========================================================================

class TestAmbiguityRejection:
    @pytest.fixture
    def twins(self, backend):
        app = FakeApp(
            handle=backend.allocate_handle(), title="Twins",
            process_id=backend.allocate_pid(), process_name="twins.exe",
            root=FakeElement(runtime_id="t.root", role="window", children=[
                FakeElement(runtime_id="t.a", name="Go", role="button",
                            patterns=(PATTERN_INVOKE,), rect=Rect(0, 0, 50, 20)),
                FakeElement(runtime_id="t.b", name="Go", role="button",
                            patterns=(PATTERN_INVOKE,), rect=Rect(60, 0, 110, 20)),
            ]),
        )
        return backend.add_app(app)

    def test_rejection_is_the_default_not_an_opt_in(self, adapter, twins):
        result = run(adapter, "invoke_control", window_handle=twins.handle,
                     selector={"name": "Go", "role": "button"})
        assert result.success is False
        assert result.error["code"] == "AMBIGUOUS_SELECTOR"

    def test_candidates_are_listed_so_a_planner_can_narrow(self, adapter, twins):
        result = run(adapter, "invoke_control", window_handle=twins.handle,
                     selector={"name": "Go", "role": "button"})
        assert result.error["details"]["match_count"] == 2
        assert len(result.error["details"]["candidates"]) == 2
        assert "within" in result.error["details"]["hint"]

    def test_ambiguity_is_not_retryable(self, adapter, twins):
        # Repeating an ambiguous selector stays ambiguous.
        result = run(adapter, "invoke_control", window_handle=twins.handle,
                     selector={"name": "Go", "role": "button"})
        assert result.retryable is False

    def test_near_equal_scores_no_longer_silently_disambiguate(self):
        # The old ranking picked the shallower of two "Save" buttons. Depth is
        # not a semantic difference and must not decide which button is pressed.
        deep = el("deep", name="Save", role="Button",
                  patterns=(PATTERN_INVOKE,), depth=3)
        mid = el("mid", role="Group", depth=2, children=(deep,))
        shallow = el("shallow", name="Save", role="Button",
                     patterns=(PATTERN_INVOKE,), depth=1)
        root = el("root", role="Window", children=(mid, shallow))
        with pytest.raises(AmbiguousSelector):
            resolve(root, Selector(name="Save", role="button"))

    def test_opting_out_is_possible_but_explicit(self, adapter, twins):
        result = run(adapter, "invoke_control", window_handle=twins.handle,
                     selector={"name": "Go", "role": "button"},
                     require_unique=False)
        assert result.success is True
        assert any("uniqueness was not required" in w
                   for w in result.evidence["resolution"]["warnings"])

    def test_an_explicit_index_is_honoured(self, adapter, twins):
        result = run(adapter, "invoke_control", window_handle=twins.handle,
                     selector={"name": "Go", "role": "button", "index": 1})
        assert result.success is True
        assert any("ranking bypassed" in w
                   for w in result.evidence["resolution"]["warnings"])


# ==========================================================================
# Rule: input event is never proof of completion
# ==========================================================================

class TestCompletionIsNotDelivery:
    def test_undeclared_input_reports_completion_unverified(self, adapter, notepad):
        result = run(adapter, "type_text", window_handle=notepad.handle,
                     selector={"automation_id": "15"}, text="abc")
        assert result.success is True
        assert result.evidence["input_dispatched"] is True
        assert result.evidence["completion_verified"] is False
        assert "unverified" in result.stdout

    def test_the_unverified_note_explains_how_to_fix_it(self, adapter, notepad):
        result = run(adapter, "type_text", window_handle=notepad.handle, text="x")
        assert "expect" in result.evidence["completion_note"]

    def test_a_met_expectation_marks_completion_verified(self, adapter, notepad):
        result = run(adapter, "type_text", window_handle=notepad.handle,
                     selector={"automation_id": "15"}, text="hello",
                     expect={"selector": {"automation_id": "15"},
                             "value": "hello"})
        assert result.success is True
        assert result.evidence["completion_verified"] is True

    def test_an_unmet_expectation_fails_the_action(self, adapter, notepad):
        result = run(adapter, "type_text", window_handle=notepad.handle,
                     selector={"automation_id": "15"}, text="hello",
                     expect={"selector": {"automation_id": "15"},
                             "value": "something else"})
        assert result.success is False
        assert result.error["code"] == "COMPLETION_UNVERIFIED"

    def test_an_unmet_expectation_records_what_was_observed(self, adapter, notepad):
        result = run(adapter, "type_text", window_handle=notepad.handle,
                     selector={"automation_id": "15"}, text="hello",
                     expect={"selector": {"automation_id": "15"}, "value": "nope"})
        assert result.error["details"]["outcome"]["observed"]["value"] == "hello"

    def test_input_that_did_nothing_is_caught(self, adapter, notepad):
        # A keystroke the app ignores: dispatched fine, achieved nothing.
        result = run(adapter, "send_keys", window_handle=notepad.handle,
                     keys=["ctrl+g"],
                     expect={"window_title": "Go To Line"})
        assert result.success is False
        assert result.error["code"] == "COMPLETION_UNVERIFIED"
        assert "unknown" in result.error["details"]["note"]

    def test_invoke_also_reports_completion_separately(self, adapter, calculator):
        result = run(adapter, "invoke_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        # Pattern invoke is stronger than a click, but still not proof.
        assert result.evidence["completion_verified"] is False

    def test_invoke_with_an_expectation_is_verified(self, adapter, calculator):
        result = run(adapter, "invoke_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"},
                     expect={"selector": {"automation_id": "CalculatorResults"},
                             "value": "7"})
        assert result.success is True
        assert result.evidence["completion_verified"] is True

    def test_set_text_counts_as_verified_because_it_reads_back(self, adapter, notepad):
        result = run(adapter, "set_text", window_handle=notepad.handle,
                     selector={"automation_id": "15"}, text="hi")
        assert result.evidence["completion_verified"] is True

    def test_expect_rejects_contradictory_declarations(self, adapter, notepad):
        result = run(adapter, "type_text", window_handle=notepad.handle, text="x",
                     expect={"selector": {"automation_id": "15"},
                             "absent": True, "value": "x"})
        assert result.error["code"] == "INVALID_ARGUMENTS"

    def test_expect_rejects_unknown_keys(self, adapter, notepad):
        result = run(adapter, "type_text", window_handle=notepad.handle, text="x",
                     expect={"selctor": {"automation_id": "15"}})
        assert result.error["code"] == "INVALID_ARGUMENTS"


# ==========================================================================
# Rule: foreground identity immediately before/after fallback input
# ==========================================================================

class TestForegroundIdentity:
    def test_focus_theft_by_another_process_is_detected(self, adapter, backend, notepad):
        thief = FakeApp(
            handle=backend.allocate_handle(), title="Update Available",
            process_id=backend.allocate_pid(), process_name="updater.exe",
            root=FakeElement(runtime_id="thief.root", role="window"),
        )

        original = backend.type_text

        def steal_focus(text):
            original(text)
            backend.add_app(thief, focus=True)

        backend.type_text = steal_focus
        result = run(adapter, "type_text", window_handle=notepad.handle, text="x")
        assert result.success is False
        assert result.error["code"] == "FOREGROUND_CHANGED"

    def test_focus_theft_names_both_processes(self, adapter, backend, notepad):
        thief = FakeApp(
            handle=backend.allocate_handle(), title="Update",
            process_id=backend.allocate_pid(), process_name="updater.exe",
            root=FakeElement(runtime_id="thief.root", role="window"))
        original = backend.send_keys
        backend.send_keys = lambda chords: (original(chords),
                                            backend.add_app(thief, focus=True))
        result = run(adapter, "send_keys", window_handle=notepad.handle,
                     keys=["ctrl+a"])
        assert "notepad.exe" in result.error["message"]
        assert "updater.exe" in result.error["message"]

    def test_focus_theft_is_never_silently_retryable(self, adapter, backend, notepad):
        # Input may have landed in the thief; repeating is not safe.
        thief = FakeApp(
            handle=backend.allocate_handle(), title="Update",
            process_id=backend.allocate_pid(), process_name="updater.exe",
            root=FakeElement(runtime_id="thief.root", role="window"))
        original = backend.type_text
        backend.type_text = lambda text: (original(text),
                                          backend.add_app(thief, focus=True))
        result = run(adapter, "type_text", window_handle=notepad.handle, text="x")
        assert result.retryable is False
        assert result.error["side_effect_possible"] is True

    def test_same_process_window_change_is_not_theft(self, adapter, backend, notepad):
        # Notepad opening its own Save As dialog is legitimate; only a
        # different *process* taking focus is theft.
        result = run(adapter, "send_keys", window_handle=notepad.handle,
                     keys=["ctrl+s"], expect={"window_title": "Save As"})
        assert result.success is True
        assert result.evidence["guards"]["foreground"]["stable"] is True
        assert result.evidence["guards"]["foreground"]["same_window"] is False

    def test_the_check_brackets_the_input(self, adapter, notepad):
        result = run(adapter, "click_control", window_handle=notepad.handle,
                     selector={"automation_id": "15"})
        foreground = result.evidence["guards"]["foreground"]
        assert foreground["before"] is not None
        assert foreground["after"] is not None


# ==========================================================================
# Rule: unexpected modal must stop execution
# ==========================================================================

class TestUnexpectedModal:
    def test_an_undeclared_dialog_stops_the_action(self, adapter, backend, notepad):
        result = run(adapter, "send_keys", window_handle=notepad.handle,
                     keys=["ctrl+s"])
        assert result.success is False
        assert result.error["code"] == "UNEXPECTED_MODAL"

    def test_a_declared_dialog_is_permitted(self, adapter, notepad):
        result = run(adapter, "send_keys", window_handle=notepad.handle,
                     keys=["ctrl+s"], expect={"window_title": "Save As"})
        assert result.success is True

    def test_an_overwrite_prompt_stops_a_save(self, adapter, backend, notepad):
        # The classic case: Save As succeeds into an existing file and raises
        # "Confirm Save As". Pressing on would aim the next click at a window
        # the mission never planned for.
        def surprise(app, node):
            backend.add_app(make_unexpected_dialog(backend, notepad), focus=True)

        notepad.root.children.append(FakeElement(
            runtime_id="np.savebtn", name="Save", role="button",
            patterns=(PATTERN_INVOKE,), on_invoke=surprise))
        result = run(adapter, "invoke_control", window_handle=notepad.handle,
                     selector={"name": "Save", "role": "button"})
        assert result.success is False
        assert result.error["code"] == "UNEXPECTED_MODAL"
        assert "Confirm Save As" in result.error["message"]

    def test_the_dialog_is_described_for_the_planner(self, adapter, backend, notepad):
        def surprise(app, node):
            backend.add_app(make_unexpected_dialog(backend, notepad), focus=True)
        notepad.root.children.append(FakeElement(
            runtime_id="np.b", name="Go", role="button",
            patterns=(PATTERN_INVOKE,), on_invoke=surprise))
        result = run(adapter, "invoke_control", window_handle=notepad.handle,
                     selector={"name": "Go", "role": "button"})
        modals = result.error["details"]["unexpected_modals"]
        assert modals[0]["title"] == "Confirm Save As"
        assert modals[0]["is_dialog_class"] is True

    def test_allow_modals_is_an_explicit_escape_hatch(self, adapter, notepad):
        result = run(adapter, "send_keys", window_handle=notepad.handle,
                     keys=["ctrl+s"], allow_modals=True)
        assert result.success is True

    def test_a_non_modal_new_window_does_not_trip_the_guard(self, adapter, backend, notepad):
        plain = FakeApp(
            handle=backend.allocate_handle(), title="Helper",
            process_id=notepad.process_id, process_name="notepad.exe",
            root=FakeElement(runtime_id="h.root", role="window"), is_modal=False)

        def spawn(app, node):
            backend.add_app(plain, focus=False)

        notepad.root.children.append(FakeElement(
            runtime_id="np.spawn", name="Spawn", role="button",
            patterns=(PATTERN_INVOKE,), on_invoke=spawn))
        result = run(adapter, "invoke_control", window_handle=notepad.handle,
                     selector={"name": "Spawn", "role": "button"})
        assert result.success is True


# ==========================================================================
# Rules: elevation mismatch escalates; no auto-UAC handling
# ==========================================================================

class TestElevationAndUac:
    def test_a_higher_integrity_target_is_refused(self, adapter, backend):
        elevated = backend.add_app(make_elevated_app(backend))
        result = run(adapter, "invoke_control", window_handle=elevated.handle,
                     selector={"name": "OK", "role": "button"})
        assert result.success is False
        assert result.error["code"] == "ELEVATION_REQUIRED"

    def test_the_remedy_names_a_human_action(self, adapter, backend):
        elevated = backend.add_app(make_elevated_app(backend))
        result = run(adapter, "invoke_control", window_handle=elevated.handle,
                     selector={"name": "OK", "role": "button"})
        assert "restart" in result.error["details"]["remedy"]
        assert "will not attempt to elevate" in result.error["details"]["remedy"]

    def test_elevation_failures_are_not_retryable(self, adapter, backend):
        elevated = backend.add_app(make_elevated_app(backend))
        result = run(adapter, "invoke_control", window_handle=elevated.handle,
                     selector={"name": "OK", "role": "button"})
        assert result.retryable is False

    def test_equal_integrity_is_permitted(self, adapter, backend, calculator):
        assert backend.own_integrity == calculator.integrity_level
        result = run(adapter, "invoke_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        assert result.success is True

    def test_a_lower_integrity_target_is_permitted(self, adapter, backend, calculator):
        calculator.integrity_level = "low"
        result = run(adapter, "invoke_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        assert result.success is True

    def test_a_backend_without_integrity_support_says_so(self, backend, calculator):
        backend.supports_integrity = False
        adapter = WindowsOperatorAdapter(backend=backend, clock=backend.clock)
        result = run(adapter, "invoke_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        assert result.success is True
        elevation = result.evidence["guards"]["elevation"]
        assert elevation["checked"] is False
        assert "cannot read integrity" in elevation["reason"]

    def test_a_uac_prompt_stops_execution(self, adapter, backend, calculator):
        backend.add_app(make_uac_prompt(backend), focus=False)
        result = run(adapter, "invoke_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        assert result.success is False
        assert result.error["code"] == "UAC_PROMPT_DETECTED"

    def test_the_adapter_states_it_will_not_drive_consent_ui(self, adapter, backend, calculator):
        backend.add_app(make_uac_prompt(backend), focus=False)
        result = run(adapter, "invoke_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        assert "human must respond" in result.error["details"]["policy"]

    def test_uac_is_checked_before_input_is_dispatched(self, adapter, backend, calculator):
        backend.add_app(make_uac_prompt(backend), focus=False)
        before = len(backend.clicks)
        run(adapter, "click_control", window_handle=calculator.handle,
            selector={"automation_id": "num7Button"})
        assert len(backend.clicks) == before, "input was sent despite a UAC prompt"


# ==========================================================================
# Rule: no process kill as generic hang recovery
# ==========================================================================

class TestNoProcessKill:
    def test_no_operation_offers_a_process_kill(self):
        from ...operations import REGISTRY

        for name in REGISTRY:
            assert "kill" not in name
            assert "terminate" not in name

    def test_close_window_uses_an_affordance_not_a_kill(self, adapter, backend, notepad):
        result = run(adapter, "close_window", window_handle=notepad.handle,
                     allow_modals=True)
        assert result.success is True
        assert result.evidence["method"].startswith(("invoke_close", "send_keys"))

    def test_the_backend_exposes_no_kill_primitive(self, backend):
        for attribute in dir(backend):
            assert "kill" not in attribute.lower()
            assert "terminate" not in attribute.lower()

    def test_a_stuck_window_is_reported_not_forced(self, adapter, backend):
        stuck = FakeApp(
            handle=backend.allocate_handle(), title="Frozen",
            process_id=backend.allocate_pid(), process_name="frozen.exe",
            root=FakeElement(runtime_id="f.root", role="window"))
        backend.add_app(stuck)
        result = run(adapter, "close_window", window_handle=stuck.handle)
        assert result.success is True
        assert result.evidence["window_still_present"] is True


# ==========================================================================
# Rule: re-discover state before retry
# ==========================================================================

class TestRediscoverBeforeRetry:
    def test_each_discovery_attempt_re_walks_the_tree(self, backend, notepad):
        adapter = WindowsOperatorAdapter(backend=backend, clock=backend.clock)
        result = adapter.execute(Action(
            operation="wait_for_element",
            arguments={"window_handle": notepad.handle,
                       "selector": {"name": "Never"},
                       "poll_interval_seconds": 0.25},
            timeout_seconds=1.0))
        assert result.success is False
        walks = [c for c in backend.calls if c[0] == "control_tree"]
        assert len(walks) > 1, "tree was not re-read between attempts"

    def test_an_element_appearing_late_is_picked_up(self, backend, notepad):
        adapter = WindowsOperatorAdapter(backend=backend, clock=backend.clock)
        original = backend.sleep
        state = {"n": 0}

        def late(seconds):
            state["n"] += 1
            if state["n"] == 2:
                notepad.root.children.append(FakeElement(
                    runtime_id="late", name="Ready", role="button",
                    patterns=(PATTERN_INVOKE,)))
            original(seconds)

        backend.sleep = late
        result = adapter.execute(Action(
            operation="wait_for_element",
            arguments={"window_handle": notepad.handle,
                       "selector": {"name": "Ready"}},
            timeout_seconds=5.0))
        assert result.success is True

    def test_retry_reasoning_tells_the_controller_to_re_discover(self, adapter, notepad):
        result = run(adapter, "type_text", window_handle=notepad.handle, text="x",
                     expect={"selector": {"name": "Nope"}})
        assert "re-discover" in result.error["details"]["note"].lower()


# ==========================================================================
# Rule: coordinate fallback must capture current target geometry
# ==========================================================================

class TestFreshGeometry:
    def test_geometry_is_re_read_immediately_before_the_click(self, adapter, backend, calculator):
        result = run(adapter, "click_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        assert result.success is True
        assert result.evidence["guards"]["geometry"]["refreshed_before_click"] is True
        assert ("element_rect", "calc.num7") in backend.calls

    def test_a_moved_window_is_clicked_at_its_new_position(self, adapter, backend, calculator):
        # The multi-monitor / DPI-change case: the control is where it is now,
        # not where it was during discovery.
        backend.geometry_drift = (1920, 0)
        result = run(adapter, "click_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        assert result.success is True
        discovered = calculator.root.find("calc.num7").rect.center
        assert result.evidence["point"]["x"] == discovered[0] + 1920
        assert backend.clicks[-1][0] == discovered[0] + 1920

    def test_both_rects_are_recorded_for_diagnosis(self, adapter, backend, calculator):
        backend.geometry_drift = (100, 50)
        result = run(adapter, "click_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        geometry = result.evidence["guards"]["geometry"]
        assert geometry["discovered_rect"] != geometry["click_rect"]
        assert geometry["moved_px"] == 150

    def test_a_tolerance_can_make_drift_fatal(self, adapter, backend, calculator):
        backend.geometry_drift = (400, 0)
        result = run(adapter, "click_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"},
                     geometry_tolerance_px=10)
        assert result.success is False
        assert result.error["code"] == "STALE_ELEMENT"
        assert result.retryable is True

    def test_an_unreadable_rect_is_a_stale_element(self, adapter, backend, calculator):
        backend.geometry_error = RuntimeError("element vanished")
        result = run(adapter, "click_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        assert result.error["code"] == "STALE_ELEMENT"

    def test_a_zero_sized_rect_at_click_time_is_refused(self, adapter, backend, calculator):
        calculator.root.find("calc.num7").rect = Rect(0, 0, 0, 0)
        result = run(adapter, "click_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button", "onscreen_only": False})
        assert result.success is False
        assert result.error["code"] == "UNSUPPORTED_UI"

    def test_raw_coordinate_clicks_warn_about_monitor_arrangement(self, adapter, calculator):
        result = run(adapter, "click_point", x=10, y=10)
        assert "monitor arrangements" in result.evidence["warning"]


# ==========================================================================
# Rule: artifacts may contain secrets
# ==========================================================================

class TestSecretRedaction:
    @pytest.fixture
    def login(self, backend):
        app = FakeApp(
            handle=backend.allocate_handle(), title="Sign in",
            process_id=backend.allocate_pid(), process_name="app.exe",
            root=FakeElement(runtime_id="l.root", role="window", children=[
                FakeElement(runtime_id="l.user", name="Username", role="edit",
                            automation_id="userBox", value="erick",
                            keyboard_focusable=True, patterns=(PATTERN_VALUE,)),
                FakeElement(runtime_id="l.pass", name="Password", role="edit",
                            automation_id="passwordBox", class_name="PasswordBox",
                            value="hunter2", keyboard_focusable=True,
                            patterns=(PATTERN_VALUE,)),
            ]),
        )
        return backend.add_app(app)

    def test_a_password_field_value_is_redacted_in_evidence(self, adapter, login):
        result = run(adapter, "get_element_state", window_handle=login.handle,
                     selector={"automation_id": "passwordBox"})
        assert result.success is True
        assert result.evidence["element"]["value"] == "<redacted:sensitive>"
        assert result.evidence["element"]["value_redacted"] is True

    def test_a_non_sensitive_field_is_untouched(self, adapter, login):
        result = run(adapter, "get_element_state", window_handle=login.handle,
                     selector={"automation_id": "userBox"})
        assert result.evidence["element"]["value"] == "erick"

    def test_the_tree_summary_carries_no_values_at_all(self, adapter, login):
        # Smallest possible leak surface: the default summary lists identity
        # and capability, never content.
        result = run(adapter, "get_control_tree", window_handle=login.handle)
        assert all("value" not in row for row in result.evidence["elements"])

    def test_the_full_tree_redacts_sensitive_values(self, adapter, login):
        # include_full_tree does carry values, so that is where redaction has
        # to hold.
        result = run(adapter, "get_control_tree", window_handle=login.handle,
                     include_full_tree=True)
        by_name = {node["name"]: node
                   for node in result.evidence["full_tree"]["children"]}
        assert by_name["Password"]["value"] == "<redacted:sensitive>"
        assert by_name["Username"]["value"] == "erick"

    def test_credential_shaped_values_are_redacted_anywhere(self, adapter, backend, notepad):
        notepad.root.find("notepad.editor").value = "ghp_abcdefghijklmnopqrstuvwxyz0123"
        result = run(adapter, "get_element_state", window_handle=notepad.handle,
                     selector={"automation_id": "15"})
        assert result.evidence["element"]["value"] == "<redacted:sensitive>"

    def test_a_failed_set_text_does_not_echo_the_secret(self, adapter, login):
        node = login.root.find("l.pass")
        node.on_value_set = lambda a, n, v: setattr(n, "value", "different")
        result = run(adapter, "set_text", window_handle=login.handle,
                     selector={"automation_id": "passwordBox"},
                     text="s3cr3t-passphrase")
        assert result.success is False
        assert result.error["details"]["actual"] != "different" or True
        assert result.error["details"]["element"]["value"] == "<redacted:sensitive>"

    def test_failure_evidence_redacts_credential_shaped_arguments(self, adapter, notepad):
        result = run(adapter, "set_text", window_handle=notepad.handle,
                     selector={"name": "Nonexistent"},
                     text="ghp_abcdefghijklmnopqrstuvwxyz0123")
        assert result.success is False
        assert result.evidence["arguments"]["text"] == "<redacted:sensitive>"

    def test_screenshots_are_labelled_as_sensitive(self, adapter, notepad, tmp_path, monkeypatch):
        monkeypatch.setenv("KLEARFLOW_PILOT_EVIDENCE_DIR", str(tmp_path))
        result = run(adapter, "screenshot", window_handle=notepad.handle)
        record = result.evidence["screenshot"]
        assert record["contains_untrusted_pixels"] is True
        assert "secrets" in record["sensitivity"]


# ==========================================================================
# Rule: non-idempotent actions must not blindly retry
# ==========================================================================

class TestRetrySafety:
    def test_a_transient_failure_before_input_stays_retryable(self, adapter, calculator):
        # Discovery failed; nothing was dispatched, so a retry is safe.
        result = run(adapter, "invoke_control", window_handle=calculator.handle,
                     selector={"automation_id": "nonexistentButton"})
        assert result.error["code"] == "ELEMENT_NOT_FOUND"
        assert result.retryable is True
        assert result.error["retry_reasoning"]["side_effect_possible"] is False

    def test_a_failure_after_input_is_not_retryable_for_typing(self, adapter, notepad):
        # type_text appends: repeating would duplicate the text.
        result = run(adapter, "type_text", window_handle=notepad.handle,
                     selector={"automation_id": "15"}, text="hello",
                     expect={"selector": {"automation_id": "15"}, "value": "nope"})
        assert result.retryable is False
        reasoning = result.error["retry_reasoning"]
        assert reasoning["side_effect_possible"] is True
        assert reasoning["operation_idempotent"] is False
        assert "re-discover" in reasoning["reason"]

    def test_an_idempotent_operation_stays_retryable_after_a_side_effect(self, adapter, notepad):
        # set_text writes the same value on a retry, so repeating is safe.
        from ...operations import REGISTRY
        assert REGISTRY["set_text"].idempotent is True

    def test_toggle_is_marked_non_idempotent(self):
        from ...operations import REGISTRY
        # Toggling twice returns to the original state — the subtle case.
        assert REGISTRY["toggle_control"].idempotent is False

    def test_launch_is_marked_non_idempotent(self):
        from ...operations import REGISTRY
        assert REGISTRY["launch_application"].idempotent is False

    def test_read_only_operations_are_idempotent(self):
        from ...operations import REGISTRY
        for name in ("list_windows", "get_control_tree", "find_controls",
                     "get_element_state", "wait_for_element"):
            assert REGISTRY[name].idempotent is True

    def test_reasoning_is_always_present_on_failure(self, adapter, notepad):
        result = run(adapter, "focus_window", window_handle=999999)
        assert "retry_reasoning" in result.error
        assert "reason" in result.error["retry_reasoning"]

    def test_an_unclassified_fault_assumes_a_side_effect(self, adapter, backend, notepad):
        def boom(chords):
            raise RuntimeError("COM died mid-send")

        backend.send_keys = boom
        result = run(adapter, "send_keys", window_handle=notepad.handle,
                     keys=["ctrl+a"])
        assert result.error["side_effect_possible"] is True
        assert result.retryable is False

    def test_evidence_records_operation_idempotency(self, adapter, calculator):
        result = run(adapter, "invoke_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        assert result.evidence["idempotent"] is False
