"""Proof missions, run against the simulated applications.

These exercise the real mission code end-to-end: selector resolution, action
ordering, verification, and failure reporting. The Notepad mission performs a
genuine filesystem write and an independent read-back, so the on-disk
assertion is not simulated.

What they do *not* prove is UIA/COM/SendInput behaviour — only
``tests/integration`` covers that, and only on Windows.

The negative tests matter most: the brief requires the proof to fail when the
file contents are wrong, so that is asserted directly rather than assumed.
"""

from __future__ import annotations

import os

import pytest

from ...adapter import WindowsOperatorAdapter
from ...fakes import FakeBackend, make_desktop, make_fake_calculator, make_fake_notepad
from ...missions import calculator_proof, notepad_proof


@pytest.fixture
def desktop() -> FakeBackend:
    return make_desktop()


@pytest.fixture
def proof_adapter(desktop: FakeBackend) -> WindowsOperatorAdapter:
    return WindowsOperatorAdapter(backend=desktop, clock=desktop.clock)


@pytest.fixture
def target(tmp_path) -> str:
    return str(tmp_path / "klearflow_pilot_proof.txt")


class TestNotepadProofHappyPath:
    def test_mission_succeeds_and_verifies(self, proof_adapter, target):
        report = notepad_proof.run(proof_adapter, file_path=target)
        assert report.success is True, report.summary()
        assert report.verified is True

    def test_file_exists_on_disk_with_the_expected_contents(self, proof_adapter, target):
        notepad_proof.run(proof_adapter, file_path=target)
        assert os.path.exists(target)
        with open(target, "rb") as handle:
            assert handle.read().decode("utf-8") == "KlearFlow Pilot"

    def test_the_expected_text_is_the_briefed_string(self):
        assert notepad_proof.EXPECTED_TEXT == "KlearFlow Pilot"

    def test_every_step_is_recorded_in_order(self, proof_adapter, target):
        report = notepad_proof.run(proof_adapter, file_path=target)
        operations = [step["operation"] for step in report.steps]
        assert operations == [
            "launch_application",
            "find_controls(editor)",
            "set_text",
            "send_keys(ctrl+s)",
            "set_text(save_as_filename)",
            "invoke_control(Save)",
            "close_window",
            "verify_file_contents",
        ]

    def test_the_editor_is_found_semantically_not_by_coordinates(self, proof_adapter, desktop, target):
        notepad_proof.run(proof_adapter, file_path=target)
        # No coordinate interaction anywhere in the mission.
        assert desktop.clicks == []

    def test_notepad_is_closed_afterwards(self, proof_adapter, desktop, target):
        notepad_proof.run(proof_adapter, file_path=target)
        assert not any(app.process_name == "notepad.exe" for app in desktop.apps)

    def test_notepad_can_be_left_open_on_request(self, proof_adapter, desktop, target):
        report = notepad_proof.run(proof_adapter, file_path=target,
                                   close_when_done=False)
        assert report.success is True
        assert any(app.process_name == "notepad.exe" for app in desktop.apps)

    def test_a_stale_file_from_a_previous_run_is_removed_first(self, proof_adapter, target):
        # Otherwise a failed save could be masked by yesterday's success.
        with open(target, "w") as handle:
            handle.write("stale contents")
        report = notepad_proof.run(proof_adapter, file_path=target)
        assert report.verified is True
        assert notepad_proof.read_back(target) == "KlearFlow Pilot"

    def test_custom_text_is_honoured(self, proof_adapter, target):
        report = notepad_proof.run(proof_adapter, file_path=target, text="Hello Pilot")
        assert report.success is True
        assert notepad_proof.read_back(target) == "Hello Pilot"

    def test_crlf_line_endings_are_normalised_not_ignored(self, proof_adapter, target):
        report = notepad_proof.run(proof_adapter, file_path=target,
                                   text="line one\nline two")
        assert report.success is True
        with open(target, "rb") as handle:
            assert b"\r\n" in handle.read()  # Notepad's real behaviour
        assert report.actual == "line one\nline two"


class TestNotepadProofFailsOnWrongContents:
    """The brief's hard requirement: wrong contents must fail the proof.

    Each sabotage below corrupts the payload *after* ``set_text`` has verified
    the control, while leaving the real Save-As dialog flow intact. That way
    the mission runs to completion and it is specifically the independent
    on-disk read-back that catches the problem — which is the assertion that
    actually matters.
    """

    @staticmethod
    def _corrupting_notepad(mangle):
        """Simulated Notepad whose editor content is mangled at save time."""
        def factory(backend):
            app = make_fake_notepad(backend)
            editor = app.root.find("notepad.editor")
            open_dialog = app.key_handlers["ctrl+s"]

            def corrupt_then_save(owner, be):
                editor.value = mangle(editor.value or "")
                open_dialog(owner, be)

            app.key_handlers["ctrl+s"] = corrupt_then_save
            return app
        return factory

    def test_fails_when_the_saved_file_contains_the_wrong_text(self, proof_adapter, desktop, target):
        desktop.launchers["notepad"] = self._corrupting_notepad(
            lambda _text: "WRONG CONTENTS")
        report = notepad_proof.run(proof_adapter, file_path=target)

        assert report.success is False
        assert report.verified is False
        assert report.actual == "WRONG CONTENTS"
        assert "mismatch" in report.failure
        # The failure came from the final verification step, not an earlier one.
        assert report.steps[-1]["operation"] == "verify_file_contents"
        assert report.steps[-1]["error_code"] == "VERIFICATION_FAILED"
        # And the bytes really are wrong on disk.
        assert notepad_proof.read_back(target) == "WRONG CONTENTS"

    def test_fails_when_the_text_is_truncated(self, proof_adapter, desktop, target):
        desktop.launchers["notepad"] = self._corrupting_notepad(lambda text: text[:5])
        report = notepad_proof.run(proof_adapter, file_path=target)

        assert report.success is False
        assert report.actual == "Klear"
        assert report.steps[-1]["operation"] == "verify_file_contents"

    def test_fails_on_a_single_character_difference(self, proof_adapter, desktop, target):
        # The check must be exact, not fuzzy.
        desktop.launchers["notepad"] = self._corrupting_notepad(
            lambda text: text.replace("Pilot", "Pilo7"))
        report = notepad_proof.run(proof_adapter, file_path=target)

        assert report.success is False
        assert report.actual == "KlearFlow Pilo7"
        assert report.steps[-1]["operation"] == "verify_file_contents"

    def test_fails_on_extra_trailing_content(self, proof_adapter, desktop, target):
        desktop.launchers["notepad"] = self._corrupting_notepad(
            lambda text: text + " and more")
        report = notepad_proof.run(proof_adapter, file_path=target)

        assert report.success is False
        assert report.steps[-1]["operation"] == "verify_file_contents"

    def test_fails_when_the_file_is_empty(self, proof_adapter, desktop, target):
        desktop.launchers["notepad"] = self._corrupting_notepad(lambda _text: "")
        report = notepad_proof.run(proof_adapter, file_path=target)

        assert report.success is False
        assert report.actual == ""
        assert report.steps[-1]["operation"] == "verify_file_contents"

    def test_fails_when_the_encoding_is_wrong(self, proof_adapter, desktop, target):
        """A byte-level read notices this; an implicit text read might not."""
        def factory(backend):
            app = make_fake_notepad(backend)
            editor = app.root.find("notepad.editor")
            open_dialog = app.key_handlers["ctrl+s"]

            def save_as_utf16(owner, be):
                open_dialog(owner, be)
                # Replace the dialog's Save handler so it writes UTF-16.
                dialog = be.foreground_app()
                save_button = dialog.root.find("saveas.save")

                def wrong_encoding(app_, _node):
                    with open(target, "wb") as handle:
                        handle.write((editor.value or "").encode("utf-16-le"))
                    owner.state["saved_path"] = target
                    be.remove_app(app_.handle)
                    be.foreground_handle = owner.handle

                save_button.on_invoke = wrong_encoding

            app.key_handlers["ctrl+s"] = save_as_utf16
            return app

        desktop.launchers["notepad"] = factory
        report = notepad_proof.run(proof_adapter, file_path=target)

        assert report.success is False
        assert report.verified is False
        assert report.actual != "KlearFlow Pilot"

    def test_fails_when_no_file_is_written_at_all(self, proof_adapter, desktop, target):
        """The Save button is pressed successfully but writes nothing."""
        def factory(backend):
            app = make_fake_notepad(backend)
            open_dialog = app.key_handlers["ctrl+s"]

            def save_that_does_nothing(owner, be):
                open_dialog(owner, be)
                dialog = be.foreground_app()

                def no_op(app_, _node):
                    be.remove_app(app_.handle)
                    be.foreground_handle = owner.handle

                dialog.root.find("saveas.save").on_invoke = no_op

            app.key_handlers["ctrl+s"] = save_that_does_nothing
            return app

        desktop.launchers["notepad"] = factory
        report = notepad_proof.run(proof_adapter, file_path=target)

        assert report.success is False
        assert report.steps[-1]["operation"] == "verify_file_exists"
        assert "was not created" in report.failure


class TestNotepadProofFailsOnBrokenUi:
    def test_reports_a_failed_launch(self, proof_adapter, target):
        report = notepad_proof.run(proof_adapter, file_path=target,
                                   notepad_command="nosuchapp.exe")
        assert report.success is False
        assert report.steps[0]["error_code"] == "LAUNCH_FAILED"
        assert report.steps[0]["retryable"] is True

    def test_reports_a_missing_editor_control(self, proof_adapter, desktop, target):
        def no_editor(backend):
            app = make_fake_notepad(backend)
            app.root.children = [c for c in app.root.children
                                 if c.runtime_id != "notepad.editor"]
            return app

        desktop.launchers["notepad"] = no_editor
        report = notepad_proof.run(proof_adapter, file_path=target)
        assert report.success is False
        assert "Value pattern" in report.failure

    def test_reports_a_disabled_editor(self, proof_adapter, desktop, target):
        def disabled(backend):
            app = make_fake_notepad(backend)
            app.root.find("notepad.editor").enabled = False
            return app

        desktop.launchers["notepad"] = disabled
        report = notepad_proof.run(proof_adapter, file_path=target)
        assert report.success is False

    def test_reports_a_save_dialog_that_never_appears(self, proof_adapter, desktop, target):
        def no_dialog(backend):
            app = make_fake_notepad(backend)
            app.key_handlers.pop("ctrl+s")
            return app

        desktop.launchers["notepad"] = no_dialog
        report = notepad_proof.run(proof_adapter, file_path=target)
        assert report.success is False
        assert report.steps[-1]["operation"] == "set_text(save_as_filename)"

    def test_report_serialises_for_a_mission_log(self, proof_adapter, target):
        import json

        report = notepad_proof.run(proof_adapter, file_path=target)
        payload = json.loads(json.dumps(report.to_dict()))
        assert payload["verified"] is True
        assert payload["file_path"] == target


class TestCalculatorProof:
    def test_mission_succeeds_and_verifies_state(self, proof_adapter):
        report = calculator_proof.run(proof_adapter)
        assert report.success is True, report.summary()
        assert report.verified is True
        assert report.actual_display == "15"

    def test_enumerates_the_major_controls(self, proof_adapter):
        report = calculator_proof.run(proof_adapter)
        assert report.controls_enumerated >= 15
        assert report.interactable_controls >= 13
        assert report.control_roles.get("button", 0) >= 13

    def test_interacts_without_any_coordinates(self, proof_adapter, desktop):
        report = calculator_proof.run(proof_adapter)
        assert report.success is True
        assert desktop.clicks == [], "mission used coordinate clicks"

    def test_uses_automation_ids_for_every_button(self, proof_adapter, desktop):
        calculator_proof.run(proof_adapter)
        invoked = [arg for name, arg in desktop.calls if name == "invoke"]
        assert invoked == ["calc.num7", "calc.plus", "calc.num8", "calc.equals"]

    def test_records_pattern_less_controls_for_future_vision_work(self, proof_adapter):
        report = calculator_proof.run(proof_adapter)
        # The simulated app includes one deliberately inaccessible surface.
        assert any("custom" in entry for entry in report.inaccessible_controls)

    def test_fails_when_the_display_shows_the_wrong_number(self, proof_adapter, desktop):
        def broken_arithmetic(backend):
            app = make_fake_calculator(backend)
            equals = app.root.find("calc.equals")
            display = app.root.find("calc.display")

            def wrong(a, node):
                a.state["display"] = "99"
                display.value = "99"
                display.name = "Display is 99"

            equals.on_invoke = wrong
            return app

        desktop.launchers["calc"] = broken_arithmetic
        report = calculator_proof.run(proof_adapter)
        assert report.success is False
        assert report.verified is False
        assert report.actual_display == "99"
        assert "mismatch" in report.failure

    def test_fails_when_a_button_is_missing(self, proof_adapter, desktop):
        def no_plus(backend):
            app = make_fake_calculator(backend)
            app.root.children = [c for c in app.root.children
                                 if c.runtime_id != "calc.plus"]
            return app

        desktop.launchers["calc"] = no_plus
        report = calculator_proof.run(proof_adapter)
        assert report.success is False
        assert report.steps[-1]["error_code"] == "ELEMENT_NOT_FOUND"

    def test_fails_when_a_button_is_disabled(self, proof_adapter, desktop):
        def disabled_equals(backend):
            app = make_fake_calculator(backend)
            app.root.find("calc.equals").enabled = False
            return app

        desktop.launchers["calc"] = disabled_equals
        report = calculator_proof.run(proof_adapter)
        assert report.success is False

    def test_fails_when_the_ui_is_entirely_inaccessible(self, proof_adapter, desktop):
        from ...fakes import FakeApp, FakeElement

        def opaque(backend):
            return FakeApp(
                handle=backend.allocate_handle(), title="Calculator",
                process_id=backend.allocate_pid(), process_name="calc.exe",
                root=FakeElement(runtime_id="opaque", name="Calculator",
                                 role="window"),
            )

        desktop.launchers["calc"] = opaque
        report = calculator_proof.run(proof_adapter)
        assert report.success is False
        assert report.steps[-1]["error_code"] == "UNSUPPORTED_UI"
        assert "vision fallback" in report.failure

    def test_reports_a_failed_launch(self, proof_adapter):
        report = calculator_proof.run(proof_adapter,
                                      calculator_command="nosuchcalc.exe")
        assert report.success is False
        assert report.steps[0]["error_code"] == "LAUNCH_FAILED"

    def test_accepts_a_display_reported_only_via_accessible_name(self, proof_adapter, desktop):
        # Real Calculator sometimes exposes the number only as "Display is 15".
        def name_only(backend):
            app = make_fake_calculator(backend)
            display = app.root.find("calc.display")
            original = app.root.find("calc.equals").on_invoke

            def equals_then_blank(a, node):
                original(a, node)
                display.value = None

            app.root.find("calc.equals").on_invoke = equals_then_blank
            return app

        desktop.launchers["calc"] = name_only
        report = calculator_proof.run(proof_adapter)
        assert report.success is True
        assert report.actual_display == "15"

    def test_report_serialises_for_a_mission_log(self, proof_adapter):
        import json

        payload = json.loads(json.dumps(calculator_proof.run(proof_adapter).to_dict()))
        assert payload["verified"] is True
