"""Operation handlers, driven through the adapter against the fake desktop.

These go through :meth:`WindowsOperatorAdapter.execute` rather than calling
handlers directly, because the Result envelope is the actual contract and it is
what the core runtime will see.
"""

from __future__ import annotations

import pytest

from ...adapter import WindowsOperatorAdapter
from ...contracts import Action
from ...fakes import FakeApp, FakeElement
from ...model import PATTERN_INVOKE, PATTERN_TOGGLE, Rect
from ...operations import REGISTRY


def run(adapter: WindowsOperatorAdapter, operation: str, **arguments):
    return adapter.execute(Action(operation=operation, arguments=arguments))


class TestRegistry:
    def test_every_lane_goal_has_an_operation(self):
        for name in [
            "list_windows", "get_foreground_window", "launch_application",
            "focus_window", "get_control_tree", "find_controls",
            "invoke_control", "set_text", "send_keys", "type_text",
            "click_control", "click_point", "screenshot", "close_window",
        ]:
            assert name in REGISTRY, f"missing operation {name}"

    def test_every_spec_is_fully_described(self):
        for name, spec in REGISTRY.items():
            assert spec.description, f"{name} has no description"
            assert callable(spec.handler)

    def test_unknown_operation_is_a_structured_failure(self, adapter):
        result = run(adapter, "teleport_user")
        assert result.success is False
        assert result.error["code"] == "UNSUPPORTED_OPERATION"
        assert result.retryable is False
        assert "teleport_user" in result.error["details"]["operation"]


class TestWindowOperations:
    def test_list_windows_enumerates(self, adapter, notepad, calculator):
        result = run(adapter, "list_windows")
        assert result.success
        titles = [w["title"] for w in result.evidence["windows"]]
        assert "Untitled - Notepad" in titles and "Calculator" in titles

    def test_list_windows_can_filter_by_title(self, adapter, notepad, calculator):
        result = run(adapter, "list_windows", title="Calc")
        assert [w["title"] for w in result.evidence["windows"]] == ["Calculator"]

    def test_list_windows_excludes_hidden_when_visible_only(self, adapter, backend, notepad):
        notepad.is_visible = False
        assert run(adapter, "list_windows").evidence["window_count"] == 0
        assert run(adapter, "list_windows", visible_only=False).evidence["window_count"] == 1

    def test_get_foreground_window_identifies_the_focused_window(self, adapter, notepad):
        result = run(adapter, "get_foreground_window")
        assert result.success
        assert result.evidence["foreground_window"]["title"] == "Untitled - Notepad"
        assert result.evidence["foreground_window"]["is_foreground"] is True

    def test_get_foreground_window_reports_absence_as_success(self, adapter, backend):
        # An idle desktop genuinely has no foreground window; that is a fact,
        # not an error.
        backend.foreground_handle = None
        result = run(adapter, "get_foreground_window")
        assert result.success
        assert result.evidence["foreground_window"] is None

    def test_focus_window_switches_by_title(self, adapter, backend, notepad, calculator):
        backend.foreground_handle = calculator.handle
        result = run(adapter, "focus_window", window_title="Notepad")
        assert result.success
        assert backend.foreground_handle == notepad.handle

    def test_focus_window_switches_by_process_name(self, adapter, backend, notepad, calculator):
        backend.foreground_handle = calculator.handle
        # "notepad" must resolve "notepad.exe": planners name apps, not binaries.
        assert run(adapter, "focus_window", process_name="notepad").success
        assert backend.foreground_handle == notepad.handle

    def test_focus_window_restores_a_minimized_window(self, adapter, notepad):
        notepad.is_minimized = True
        assert run(adapter, "focus_window", window_handle=notepad.handle).success
        assert notepad.is_minimized is False

    def test_focus_failure_is_reported_not_assumed(self, adapter, backend, notepad, calculator):
        # Silently claiming focus succeeded would send later keystrokes to the
        # wrong application — the worst outcome for this lane.
        backend.foreground_handle = calculator.handle
        notepad.refuses_focus = True
        result = run(adapter, "focus_window", window_handle=notepad.handle)
        assert result.success is False
        assert result.error["code"] == "ELEMENT_NOT_INTERACTABLE"
        assert result.retryable is True

    def test_unknown_window_handle_is_window_not_found(self, adapter, notepad):
        result = run(adapter, "focus_window", window_handle=999999)
        assert result.error["code"] == "WINDOW_NOT_FOUND"
        assert result.retryable is True

    def test_unmatched_title_is_window_not_found(self, adapter, notepad):
        result = run(adapter, "focus_window", window_title="Photoshop")
        assert result.error["code"] == "WINDOW_NOT_FOUND"


class TestLaunch:
    def test_launches_and_reports_the_window(self, adapter):
        result = run(adapter, "launch_application", command="notepad.exe")
        assert result.success
        assert result.evidence["window"]["title"] == "Untitled - Notepad"
        assert result.evidence["process_id"] > 0

    def test_missing_command_is_invalid_arguments(self, adapter):
        result = run(adapter, "launch_application")
        assert result.error["code"] == "INVALID_ARGUMENTS"
        assert result.error["details"]["missing_argument"] == "command"

    def test_empty_command_is_rejected(self, adapter):
        assert run(adapter, "launch_application",
                   command="   ").error["code"] == "INVALID_ARGUMENTS"

    def test_arguments_must_be_a_list_not_a_string(self, adapter):
        # Accepting a string would imply shell splitting, which this lane does
        # not do; failing loudly is safer than guessing a split.
        result = run(adapter, "launch_application", command="notepad.exe",
                     arguments="a b c")
        assert result.error["code"] == "INVALID_ARGUMENTS"

    def test_unknown_program_is_launch_failed_and_retryable(self, adapter):
        result = run(adapter, "launch_application", command="nosuchapp.exe")
        assert result.error["code"] == "LAUNCH_FAILED"
        assert result.retryable is True

    def test_missing_executable_maps_to_launch_failed(self, adapter, backend):
        backend.launch_failures["notepad"] = FileNotFoundError("no such file")
        result = run(adapter, "launch_application", command="notepad.exe")
        assert result.error["code"] == "LAUNCH_FAILED"


class TestControlTree:
    def test_enumerates_the_tree_with_stats(self, adapter, calculator):
        result = run(adapter, "get_control_tree", window_handle=calculator.handle)
        assert result.success
        stats = result.evidence["stats"]
        assert stats["total_elements"] > 10
        assert stats["interactable_elements"] > 0
        assert "button" in stats["roles"]

    def test_reports_truncation(self, adapter, calculator):
        result = run(adapter, "get_control_tree",
                     window_handle=calculator.handle, limit=3)
        assert result.evidence["truncated"] is True
        assert len(result.evidence["elements"]) == 3

    def test_full_tree_is_opt_in(self, adapter, calculator):
        assert "full_tree" not in run(
            adapter, "get_control_tree", window_handle=calculator.handle).evidence
        assert "full_tree" in run(
            adapter, "get_control_tree", window_handle=calculator.handle,
            include_full_tree=True).evidence

    def test_max_depth_is_honoured(self, adapter, calculator):
        shallow = run(adapter, "get_control_tree",
                      window_handle=calculator.handle, max_depth=0)
        assert shallow.evidence["stats"]["total_elements"] == 1

    def test_flags_an_inaccessible_window(self, adapter, backend):
        # Goal 13: a window whose whole tree is one opaque node.
        opaque = FakeApp(
            handle=backend.allocate_handle(), title="Custom Renderer",
            process_id=backend.allocate_pid(), process_name="game.exe",
            root=FakeElement(runtime_id="opaque.root", name="Custom Renderer",
                             role="window", class_name="UnrealWindow"),
        )
        backend.add_app(opaque)
        result = run(adapter, "get_control_tree", window_handle=opaque.handle)
        assert result.success
        assert "vision fallback" in result.evidence["accessibility_warning"]

    def test_defaults_to_the_foreground_window(self, adapter, notepad):
        result = run(adapter, "get_control_tree")
        assert result.success
        assert result.evidence["window"]["title"] == "Untitled - Notepad"


class TestFindControls:
    def test_finds_by_name(self, adapter, calculator):
        result = run(adapter, "find_controls", window_handle=calculator.handle,
                     selector={"name": "Seven", "role": "button"})
        assert result.evidence["match_count"] == 1

    def test_finds_by_automation_id(self, adapter, calculator):
        result = run(adapter, "find_controls", window_handle=calculator.handle,
                     selector={"automation_id": "plusButton"})
        assert result.evidence["matches"][0]["name"] == "Plus"

    def test_finds_by_role_only(self, adapter, calculator):
        result = run(adapter, "find_controls", window_handle=calculator.handle,
                     selector={"role": "button"}, limit=100)
        assert result.evidence["match_count"] >= 13

    def test_accepts_flat_selector_criteria(self, adapter, calculator):
        # {"name": ..., "role": ...} at the top level, for readable actions.
        result = run(adapter, "find_controls", window_handle=calculator.handle,
                     name="Equals", role="button")
        assert result.evidence["match_count"] == 1

    def test_results_carry_scores_for_planner_inspection(self, adapter, calculator):
        result = run(adapter, "find_controls", window_handle=calculator.handle,
                     selector={"role": "button"})
        assert all("score" in row for row in result.evidence["matches"])

    def test_no_matches_is_a_successful_empty_answer(self, adapter, calculator):
        # find_controls answers a question; zero is a valid answer.
        result = run(adapter, "find_controls", window_handle=calculator.handle,
                     selector={"name": "Integrate"})
        assert result.success
        assert result.evidence["match_count"] == 0

    def test_missing_selector_is_invalid_arguments(self, adapter, calculator):
        result = run(adapter, "find_controls", window_handle=calculator.handle)
        assert result.error["code"] == "INVALID_ARGUMENTS"


class TestInvoke:
    def test_invokes_a_button_by_automation_id(self, adapter, calculator):
        result = run(adapter, "invoke_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        assert result.success
        assert calculator.state["display"] == "7"
        assert result.evidence["interaction_method"] == "invoke"

    def test_uses_the_accessibility_pattern_not_coordinates(self, adapter, backend, calculator):
        run(adapter, "invoke_control", window_handle=calculator.handle,
            selector={"automation_id": "num7Button"})
        assert ("invoke", "calc.num7") in backend.calls
        assert backend.clicks == []

    def test_missing_control_is_element_not_found_and_retryable(self, adapter, calculator):
        result = run(adapter, "invoke_control", window_handle=calculator.handle,
                     selector={"automation_id": "integrateButton"})
        assert result.error["code"] == "ELEMENT_NOT_FOUND"
        assert result.retryable is True

    def test_disabled_control_is_not_interactable(self, adapter, calculator):
        calculator.root.find("calc.equals").enabled = False
        result = run(adapter, "invoke_control", window_handle=calculator.handle,
                     selector={"automation_id": "equalButton", "enabled_only": False})
        assert result.error["code"] == "ELEMENT_NOT_INTERACTABLE"

    def test_pattern_less_control_is_unsupported_ui(self, adapter, calculator):
        # Goal 13, and the hand-off point for a vision fallback.
        result = run(adapter, "invoke_control", window_handle=calculator.handle,
                     selector={"class_name": "DirectUIHWND"})
        assert result.error["code"] == "UNSUPPORTED_UI"
        assert result.error["details"]["advertised_patterns"] == []
        assert "vision" in result.error["details"]["fallback"]

    def test_ambiguity_can_be_made_fatal(self, adapter, backend):
        twins = FakeApp(
            handle=backend.allocate_handle(), title="Twins",
            process_id=backend.allocate_pid(), process_name="twins.exe",
            root=FakeElement(runtime_id="t.root", role="window", children=[
                FakeElement(runtime_id="t.a", name="Go", role="button",
                            patterns=(PATTERN_INVOKE,)),
                FakeElement(runtime_id="t.b", name="Go", role="button",
                            patterns=(PATTERN_INVOKE,)),
            ]),
        )
        backend.add_app(twins)
        result = run(adapter, "invoke_control", window_handle=twins.handle,
                     selector={"name": "Go", "role": "button"},
                     require_unique=True)
        assert result.error["code"] == "AMBIGUOUS_SELECTOR"
        assert result.retryable is False

    def test_falls_back_to_select_item_for_a_selection_only_element(self, adapter, backend):
        from ...model import PATTERN_SELECTION_ITEM

        app = FakeApp(
            handle=backend.allocate_handle(), title="List",
            process_id=backend.allocate_pid(), process_name="list.exe",
            root=FakeElement(runtime_id="l.root", role="window", children=[
                FakeElement(runtime_id="l.item", name="Row 1", role="list_item",
                            patterns=(PATTERN_SELECTION_ITEM,)),
            ]),
        )
        backend.add_app(app)
        result = run(adapter, "invoke_control", window_handle=app.handle,
                     selector={"name": "Row 1"})
        assert result.success
        assert result.evidence["interaction_method"] == "select_item"


class TestSetText:
    def test_sets_a_value_via_the_pattern(self, adapter, notepad):
        result = run(adapter, "set_text", window_handle=notepad.handle,
                     selector={"automation_id": "15"}, text="hello")
        assert result.success
        assert notepad.root.find("notepad.editor").value == "hello"

    def test_verification_catches_a_value_that_did_not_stick(self, adapter, notepad):
        # The core requirement: a silent no-op must not read as success.
        editor = notepad.root.find("notepad.editor")
        editor.on_value_set = lambda app, node, value: setattr(node, "value", "WRONG")
        result = run(adapter, "set_text", window_handle=notepad.handle,
                     selector={"automation_id": "15"}, text="hello")
        assert result.success is False
        assert result.error["code"] == "VERIFICATION_FAILED"
        assert result.error["details"]["expected"] == "hello"
        assert result.error["details"]["actual"] == "WRONG"

    def test_verification_can_be_disabled(self, adapter, notepad):
        editor = notepad.root.find("notepad.editor")
        editor.on_value_set = lambda app, node, value: setattr(node, "value", "WRONG")
        assert run(adapter, "set_text", window_handle=notepad.handle,
                   selector={"automation_id": "15"}, text="x", verify=False).success

    def test_read_only_control_is_not_interactable(self, adapter, notepad):
        notepad.root.find("notepad.editor").read_only = True
        result = run(adapter, "set_text", window_handle=notepad.handle,
                     selector={"automation_id": "15"}, text="x")
        assert result.error["code"] == "ELEMENT_NOT_INTERACTABLE"

    def test_control_without_a_value_pattern_is_unsupported_ui(self, adapter, calculator):
        result = run(adapter, "set_text", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"}, text="x")
        assert result.error["code"] == "UNSUPPORTED_UI"

    def test_missing_text_is_invalid_arguments(self, adapter, notepad):
        result = run(adapter, "set_text", window_handle=notepad.handle,
                     selector={"automation_id": "15"})
        assert result.error["code"] == "INVALID_ARGUMENTS"

    def test_non_string_text_is_rejected(self, adapter, notepad):
        result = run(adapter, "set_text", window_handle=notepad.handle,
                     selector={"automation_id": "15"}, text=42)
        assert result.error["code"] == "INVALID_ARGUMENTS"

    def test_empty_string_is_a_legitimate_value(self, adapter, notepad):
        notepad.root.find("notepad.editor").value = "old"
        assert run(adapter, "set_text", window_handle=notepad.handle,
                   selector={"automation_id": "15"}, text="").success
        assert notepad.root.find("notepad.editor").value == ""


class TestTypeAndKeys:
    def test_type_text_appends_to_the_focused_control(self, adapter, notepad):
        result = run(adapter, "type_text", window_handle=notepad.handle,
                     selector={"automation_id": "15"}, text="abc")
        assert result.success
        assert notepad.root.find("notepad.editor").value == "abc"

    def test_type_text_reports_the_character_count(self, adapter, notepad):
        result = run(adapter, "type_text", window_handle=notepad.handle, text="hello")
        assert result.evidence["typed_characters"] == 5

    def test_type_text_rejects_non_strings(self, adapter, notepad):
        assert run(adapter, "type_text", text=None).error["code"] == "INVALID_ARGUMENTS"

    def test_send_keys_dispatches_the_chord(self, adapter, backend, notepad):
        result = run(adapter, "send_keys", window_handle=notepad.handle,
                     keys=["ctrl+s"])
        assert result.success
        assert "ctrl+s" in backend.keys_sent
        assert result.evidence["keys_description"] == "ctrl+s"

    def test_send_keys_reaches_the_application_handler(self, adapter, backend, notepad):
        run(adapter, "send_keys", window_handle=notepad.handle, keys=["ctrl+s"])
        # ctrl+s opens the simulated Save As dialog.
        assert any(w.title == "Save As" for w in backend.apps)

    def test_send_keys_accepts_a_bare_string(self, adapter, backend, notepad):
        assert run(adapter, "send_keys", keys="ctrl+a").success

    def test_send_keys_rejects_a_bad_chord(self, adapter, notepad):
        result = run(adapter, "send_keys", keys=["ctrl+nonsense"])
        assert result.error["code"] == "INVALID_ARGUMENTS"

    def test_missing_keys_is_invalid_arguments(self, adapter, notepad):
        assert run(adapter, "send_keys").error["code"] == "INVALID_ARGUMENTS"


class TestMouseFallback:
    def test_click_control_locates_semantically_then_clicks_the_centre(self, adapter, backend, calculator):
        result = run(adapter, "click_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        assert result.success
        # No coordinates were supplied by the caller; they came from the element.
        expected = calculator.root.find("calc.num7").rect.center
        assert result.evidence["point"] == {"x": expected[0], "y": expected[1]}
        assert backend.clicks[0][:2] == expected

    def test_click_control_marks_itself_as_a_fallback(self, adapter, calculator):
        result = run(adapter, "click_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        assert result.evidence["fallback_used"] == "coordinate_click"

    def test_click_control_actually_drives_the_app(self, adapter, calculator):
        run(adapter, "click_control", window_handle=calculator.handle,
            selector={"automation_id": "num7Button"})
        assert calculator.state["display"] == "7"

    def test_click_control_rejects_a_zero_sized_element(self, adapter, calculator):
        calculator.root.find("calc.num7").rect = Rect(0, 0, 0, 0)
        result = run(adapter, "click_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        assert result.error["code"] == "UNSUPPORTED_UI"

    def test_click_point_warns_about_portability(self, adapter, calculator):
        result = run(adapter, "click_point", x=10, y=20)
        assert result.success
        assert result.evidence["fallback_used"] == "raw_coordinate_click"
        assert "not portable" in result.evidence["warning"]

    @pytest.mark.parametrize("button", ["left", "right", "middle"])
    def test_supported_buttons(self, adapter, calculator, button):
        assert run(adapter, "click_point", x=1, y=1, button=button).success

    def test_unsupported_button_is_rejected(self, adapter, calculator):
        result = run(adapter, "click_point", x=1, y=1, button="thumb")
        assert result.error["code"] == "INVALID_ARGUMENTS"

    def test_double_click_is_recorded(self, adapter, backend, calculator):
        run(adapter, "click_point", x=5, y=5, double=True)
        assert backend.clicks[-1][3] is True

    def test_non_integer_coordinates_are_rejected(self, adapter, calculator):
        assert run(adapter, "click_point", x="left",
                   y=1).error["code"] == "INVALID_ARGUMENTS"


class TestToggleExpandSelect:
    def test_toggle_flips_a_checkbox(self, adapter, backend):
        app = FakeApp(
            handle=backend.allocate_handle(), title="Options",
            process_id=backend.allocate_pid(), process_name="opt.exe",
            root=FakeElement(runtime_id="o.root", role="window", children=[
                FakeElement(runtime_id="o.chk", name="Word wrap", role="check_box",
                            value="off", patterns=(PATTERN_TOGGLE,)),
            ]),
        )
        backend.add_app(app)
        result = run(adapter, "toggle_control", window_handle=app.handle,
                     selector={"name": "Word wrap"})
        assert result.success
        assert result.evidence["element_after"]["value"] == "on"

    def test_toggle_on_a_non_toggle_is_unsupported_ui(self, adapter, calculator):
        result = run(adapter, "toggle_control", window_handle=calculator.handle,
                     selector={"automation_id": "num7Button"})
        assert result.error["code"] == "UNSUPPORTED_UI"

    def test_expand_opens_a_menu(self, adapter, notepad):
        result = run(adapter, "expand_control", window_handle=notepad.handle,
                     selector={"name": "File", "role": "menu_item"}, expand=True)
        assert result.success
        assert notepad.root.find("notepad.menu.file").value == "expanded"

    def test_collapse_closes_it(self, adapter, notepad):
        run(adapter, "expand_control", window_handle=notepad.handle,
            selector={"name": "File"}, expand=True)
        run(adapter, "expand_control", window_handle=notepad.handle,
            selector={"name": "File"}, expand=False)
        assert notepad.root.find("notepad.menu.file").value == "collapsed"


class TestGetElementState:
    def test_reads_live_properties(self, adapter, calculator):
        result = run(adapter, "get_element_state", window_handle=calculator.handle,
                     selector={"automation_id": "CalculatorResults"})
        assert result.success
        assert result.evidence["element"]["value"] == "0"

    def test_reflects_a_change_made_by_an_earlier_action(self, adapter, calculator):
        run(adapter, "invoke_control", window_handle=calculator.handle,
            selector={"automation_id": "num7Button"})
        result = run(adapter, "get_element_state", window_handle=calculator.handle,
                     selector={"automation_id": "CalculatorResults"})
        assert result.evidence["element"]["value"] == "7"


class TestCloseWindow:
    def test_closes_via_keys_when_no_close_button_exists(self, adapter, backend, notepad):
        result = run(adapter, "close_window", window_handle=notepad.handle)
        assert result.success
        assert result.evidence["window_still_present"] is False
        assert notepad.handle not in [a.handle for a in backend.apps]

    def test_prefers_an_accessible_close_button(self, adapter, backend):
        closed: list[str] = []
        app = FakeApp(
            handle=backend.allocate_handle(), title="Dialog",
            process_id=backend.allocate_pid(), process_name="d.exe",
            root=FakeElement(runtime_id="d.root", role="window", children=[
                FakeElement(runtime_id="d.close", name="Close", role="button",
                            patterns=(PATTERN_INVOKE,),
                            on_invoke=lambda a, n: closed.append("clicked")),
            ]),
        )
        backend.add_app(app)
        result = run(adapter, "close_window", window_handle=app.handle)
        assert result.evidence["method"] == "invoke_close_button"
        assert closed == ["clicked"]

    def test_reports_a_window_that_refused_to_close(self, adapter, backend):
        app = FakeApp(
            handle=backend.allocate_handle(), title="Sticky",
            process_id=backend.allocate_pid(), process_name="s.exe",
            root=FakeElement(runtime_id="s.root", role="window"),
        )
        backend.add_app(app)  # no alt+f4 handler: nothing happens
        result = run(adapter, "close_window", window_handle=app.handle)
        assert result.success
        assert result.evidence["window_still_present"] is True


class TestScreenshot:
    def test_captures_a_file(self, adapter, notepad, tmp_path, monkeypatch):
        monkeypatch.setenv("KLEARFLOW_PILOT_EVIDENCE_DIR", str(tmp_path))
        result = run(adapter, "screenshot", window_handle=notepad.handle)
        assert result.success
        assert result.screenshots and result.screenshots[0].endswith(".png")

    def test_unsupported_backend_yields_unsupported_operation(self, notepad, backend):
        backend.supports_screenshots = False
        adapter = WindowsOperatorAdapter(backend=backend, clock=backend.clock)
        result = run(adapter, "screenshot")
        assert result.success is False
        assert result.error["code"] == "UNSUPPORTED_OPERATION"


class TestCapabilitiesOperation:
    def test_reports_the_backend_and_operation_set(self, adapter):
        result = run(adapter, "capabilities")
        assert result.success
        assert result.evidence["capabilities"]["ui_automation"] is True
        assert "set_text" in result.evidence["operations"]
