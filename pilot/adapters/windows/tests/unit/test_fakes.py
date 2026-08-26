"""Self-tests for the simulated backend.

The fake is test infrastructure, so its own fidelity needs pinning. If the
simulation drifts from the interaction contract it claims to mirror, the unit
suite above it would keep passing while proving less — these tests are what
stop that.
"""

from __future__ import annotations

import pytest

from ...backend import UiaBackend
from ...errors import ElementNotFound, UnsupportedUi, WindowNotFound
from ...fakes import (
    FakeBackend, make_desktop, make_fake_calculator, make_fake_notepad,
)
from ...model import PATTERN_INVOKE, PATTERN_VALUE


class TestProtocolConformance:
    def test_the_fake_satisfies_the_backend_protocol(self):
        # runtime_checkable Protocol: verifies the method set, which is what
        # keeps the fake and the real backend interchangeable.
        assert isinstance(FakeBackend(), UiaBackend)

    def test_the_null_backend_satisfies_the_protocol(self):
        from ...backend import NullBackend

        assert isinstance(NullBackend("reason"), UiaBackend)

    def test_every_protocol_method_exists_on_the_fake(self):
        for name in [
            "capabilities", "list_windows", "foreground_window", "focus_window",
            "launch", "control_tree", "refresh", "invoke", "set_value",
            "focus_element", "toggle", "select_item", "expand", "send_keys",
            "type_text", "click_point", "screenshot", "sleep",
        ]:
            assert callable(getattr(FakeBackend(), name)), name


class TestVirtualClock:
    def test_sleep_advances_the_clock_without_real_delay(self):
        backend = FakeBackend()
        start = backend.clock()
        backend.sleep(5.0)
        assert backend.clock() == start + 5.0
        assert backend.slept == 5.0

    def test_negative_sleep_is_ignored(self):
        backend = FakeBackend()
        start = backend.clock()
        backend.sleep(-1)
        assert backend.clock() == start


class TestFakeNotepadFidelity:
    def test_exposes_a_document_editor_with_value_and_text_patterns(self):
        backend = make_desktop()
        app = backend.add_app(make_fake_notepad(backend))
        editor = app.root.find("notepad.editor")
        assert editor.role == "document"
        assert editor.automation_id == "15"  # real Notepad's editor id
        assert PATTERN_VALUE in editor.patterns
        assert editor.keyboard_focusable

    def test_ctrl_s_opens_a_save_as_dialog_the_first_time(self):
        backend = make_desktop()
        backend.add_app(make_fake_notepad(backend))
        from ...keyboard import parse_keys

        backend.send_keys(parse_keys("ctrl+s"))
        assert any(w.title == "Save As" for w in backend.apps)

    def test_the_dialog_exposes_a_filename_edit_and_a_save_button(self):
        backend = make_desktop()
        backend.add_app(make_fake_notepad(backend))
        from ...keyboard import parse_keys

        backend.send_keys(parse_keys("ctrl+s"))
        dialog = backend.foreground_app()
        filename = dialog.root.find("saveas.filename")
        save = dialog.root.find("saveas.save")
        assert filename.automation_id == "1001"  # classic common-dialog id
        assert PATTERN_VALUE in filename.patterns
        assert save.name == "Save" and PATTERN_INVOKE in save.patterns

    def test_saving_writes_the_editor_content_to_disk(self, tmp_path):
        backend = make_desktop()
        app = backend.add_app(make_fake_notepad(backend))
        from ...keyboard import parse_keys

        app.root.find("notepad.editor").value = "payload"
        backend.send_keys(parse_keys("ctrl+s"))
        dialog = backend.foreground_app()
        target = str(tmp_path / "out.txt")
        dialog.root.find("saveas.filename").value = target
        dialog.root.find("saveas.save").on_invoke(dialog, dialog.root.find("saveas.save"))
        with open(target, "rb") as handle:
            assert handle.read() == b"payload"

    def test_saving_uses_crlf_like_real_notepad(self, tmp_path):
        backend = make_desktop()
        app = backend.add_app(make_fake_notepad(backend))
        from ...keyboard import parse_keys

        app.root.find("notepad.editor").value = "a\nb"
        backend.send_keys(parse_keys("ctrl+s"))
        dialog = backend.foreground_app()
        target = str(tmp_path / "out.txt")
        dialog.root.find("saveas.filename").value = target
        dialog.root.find("saveas.save").on_invoke(dialog, dialog.root.find("saveas.save"))
        with open(target, "rb") as handle:
            assert handle.read() == b"a\r\nb"

    def test_saving_retitles_the_window(self, tmp_path):
        backend = make_desktop()
        app = backend.add_app(make_fake_notepad(backend))
        from ...keyboard import parse_keys

        backend.send_keys(parse_keys("ctrl+s"))
        dialog = backend.foreground_app()
        dialog.root.find("saveas.filename").value = str(tmp_path / "doc.txt")
        dialog.root.find("saveas.save").on_invoke(dialog, dialog.root.find("saveas.save"))
        assert app.title == "doc.txt - Notepad"

    def test_a_second_save_writes_in_place_without_a_dialog(self, tmp_path):
        backend = make_desktop()
        app = backend.add_app(make_fake_notepad(backend))
        from ...keyboard import parse_keys

        target = str(tmp_path / "doc.txt")
        backend.send_keys(parse_keys("ctrl+s"))
        dialog = backend.foreground_app()
        dialog.root.find("saveas.filename").value = target
        dialog.root.find("saveas.save").on_invoke(dialog, dialog.root.find("saveas.save"))

        app.root.find("notepad.editor").value = "updated"
        backend.foreground_handle = app.handle
        backend.send_keys(parse_keys("ctrl+s"))
        assert not any(w.title == "Save As" for w in backend.apps)
        with open(target, "rb") as handle:
            assert handle.read() == b"updated"

    def test_an_empty_filename_leaves_the_dialog_open(self):
        backend = make_desktop()
        backend.add_app(make_fake_notepad(backend))
        from ...keyboard import parse_keys

        backend.send_keys(parse_keys("ctrl+s"))
        dialog = backend.foreground_app()
        dialog.root.find("saveas.save").on_invoke(dialog, dialog.root.find("saveas.save"))
        assert any(w.title == "Save As" for w in backend.apps)

    def test_cancel_closes_the_dialog_without_writing(self, tmp_path):
        backend = make_desktop()
        app = backend.add_app(make_fake_notepad(backend))
        from ...keyboard import parse_keys

        backend.send_keys(parse_keys("ctrl+s"))
        dialog = backend.foreground_app()
        target = str(tmp_path / "never.txt")
        dialog.root.find("saveas.filename").value = target
        dialog.root.find("saveas.cancel").on_invoke(dialog, dialog.root.find("saveas.cancel"))
        assert not any(w.title == "Save As" for w in backend.apps)
        assert backend.foreground_handle == app.handle
        import os
        assert not os.path.exists(target)

    def test_alt_f4_closes_notepad(self):
        backend = make_desktop()
        app = backend.add_app(make_fake_notepad(backend))
        from ...keyboard import parse_keys

        backend.send_keys(parse_keys("alt+f4"))
        assert app.handle not in [a.handle for a in backend.apps]

    def test_typing_appends_to_the_focused_editor(self):
        backend = make_desktop()
        app = backend.add_app(make_fake_notepad(backend))
        backend.type_text("ab")
        backend.type_text("c")
        assert app.root.find("notepad.editor").value == "abc"

    def test_typing_into_a_read_only_control_is_ignored(self):
        backend = make_desktop()
        app = backend.add_app(make_fake_notepad(backend))
        app.root.find("notepad.editor").read_only = True
        backend.type_text("x")
        assert app.root.find("notepad.editor").value == ""


class TestFakeCalculatorFidelity:
    def test_uses_real_automation_ids(self):
        backend = make_desktop()
        app = backend.add_app(make_fake_calculator(backend))
        ids = {node.automation_id for node in app.root.walk()}
        assert {"num7Button", "num8Button", "plusButton", "equalButton",
                "CalculatorResults"} <= ids

    def test_display_name_follows_the_real_accessible_pattern(self):
        backend = make_desktop()
        app = backend.add_app(make_fake_calculator(backend))
        assert app.root.find("calc.display").name == "Display is 0"

    def test_arithmetic_updates_the_display(self):
        backend = make_desktop()
        app = backend.add_app(make_fake_calculator(backend))
        for runtime_id in ("calc.num7", "calc.plus", "calc.num8", "calc.equals"):
            node = app.root.find(runtime_id)
            node.on_invoke(app, node)
        assert app.state["display"] == "15"
        assert app.root.find("calc.display").value == "15"
        assert app.root.find("calc.display").name == "Display is 15"

    def test_multi_digit_entry_concatenates(self):
        backend = make_desktop()
        app = backend.add_app(make_fake_calculator(backend))
        for runtime_id in ("calc.num1", "calc.num2", "calc.num3"):
            node = app.root.find(runtime_id)
            node.on_invoke(app, node)
        assert app.state["display"] == "123"

    def test_clear_resets_state(self):
        backend = make_desktop()
        app = backend.add_app(make_fake_calculator(backend))
        seven = app.root.find("calc.num7")
        seven.on_invoke(app, seven)
        clear = app.root.find("calc.clear")
        clear.on_invoke(app, clear)
        assert app.state["display"] == "0"

    def test_includes_a_pattern_less_surface_for_goal_13(self):
        backend = make_desktop()
        app = backend.add_app(make_fake_calculator(backend))
        assert app.root.find("calc.custom_surface").patterns == ()


class TestFakeErrorPaths:
    def test_unknown_window_raises_window_not_found(self):
        with pytest.raises(WindowNotFound):
            make_desktop().app(12345)

    def test_unknown_element_raises_element_not_found(self):
        backend = make_desktop()
        backend.add_app(make_fake_notepad(backend))
        with pytest.raises(ElementNotFound):
            backend._owner_of("does.not.exist")

    def test_pattern_enforcement_raises_unsupported_ui(self):
        backend = make_desktop()
        app = backend.add_app(make_fake_calculator(backend))
        snapshot = backend.control_tree(window_handle=app.handle)
        surface = next(n for n in snapshot.walk()
                       if n.runtime_id == "calc.custom_surface")
        with pytest.raises(UnsupportedUi):
            backend.invoke(surface)

    def test_launch_failures_can_be_injected(self):
        backend = make_desktop()
        backend.launch_failures["notepad"] = FileNotFoundError("gone")
        with pytest.raises(FileNotFoundError):
            backend.launch("notepad.exe")

    def test_control_tree_without_a_foreground_window_raises(self):
        backend = FakeBackend()
        with pytest.raises(WindowNotFound):
            backend.control_tree()


class TestFakeCallLog:
    def test_records_how_an_interaction_was_performed(self):
        # Lets tests assert pattern-based interaction rather than coordinates.
        backend = make_desktop()
        app = backend.add_app(make_fake_calculator(backend))
        snapshot = backend.control_tree(window_handle=app.handle)
        seven = next(n for n in snapshot.walk() if n.runtime_id == "calc.num7")
        backend.invoke(seven)
        assert ("invoke", "calc.num7") in backend.calls
        assert backend.clicks == []

    def test_coordinate_clicks_are_recorded_separately(self):
        backend = make_desktop()
        backend.add_app(make_fake_calculator(backend))
        backend.click_point(60, 380, button="left")
        assert backend.clicks == [(60, 380, "left", False)]
