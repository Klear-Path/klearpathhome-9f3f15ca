"""Chord parsing."""

from __future__ import annotations

import pytest

from ...errors import InvalidArguments
from ...keyboard import (
    MOD_ALT, MOD_CTRL, MOD_SHIFT, MOD_WIN,
    describe_keys, parse_chord, parse_keys,
)


class TestParseChord:
    @pytest.mark.parametrize("spec,key,mods", [
        ("a", "a", ()),
        ("A", "A", ()),
        ("ctrl+s", "s", (MOD_CTRL,)),
        ("CTRL+S", "S", (MOD_CTRL,)),
        ("control+s", "s", (MOD_CTRL,)),
        ("ctrl+shift+s", "s", (MOD_CTRL, MOD_SHIFT)),
        ("shift+ctrl+s", "s", (MOD_CTRL, MOD_SHIFT)),
        ("alt+f4", "f4", (MOD_ALT,)),
        ("win+r", "r", (MOD_WIN,)),
        ("enter", "enter", ()),
        ("Return", "enter", ()),
        ("esc", "escape", ()),
        ("pgdn", "page_down", ()),
        ("f12", "f12", ()),
        ("ctrl+alt+shift+win+x", "x", (MOD_CTRL, MOD_ALT, MOD_SHIFT, MOD_WIN)),
    ])
    def test_parses_valid_chords(self, spec, key, mods):
        chord = parse_chord(spec)
        assert chord.key == key
        assert chord.modifiers == mods

    def test_modifier_order_is_canonical_regardless_of_input_order(self):
        # Equal chords must compare equal so evidence is stable.
        assert parse_chord("shift+alt+ctrl+p") == parse_chord("ctrl+alt+shift+p")

    def test_whitespace_is_tolerated(self):
        assert parse_chord("  ctrl+s  ") == parse_chord("ctrl+s")

    def test_trailing_plus_is_a_literal_plus_key(self):
        chord = parse_chord("ctrl++")
        assert chord.key == "+"
        assert chord.modifiers == (MOD_CTRL,)

    def test_bare_plus_is_a_literal_plus_key(self):
        assert parse_chord("+").key == "+"

    @pytest.mark.parametrize("spec", ["", "   ", None, 42])
    def test_rejects_empty_or_non_string(self, spec):
        with pytest.raises(InvalidArguments):
            parse_chord(spec)

    def test_rejects_a_chord_with_only_modifiers(self):
        with pytest.raises(InvalidArguments) as info:
            parse_chord("ctrl+alt")
        assert "no key" in str(info.value)

    def test_rejects_an_unknown_multi_character_key(self):
        with pytest.raises(InvalidArguments) as info:
            parse_chord("ctrl+banana")
        assert info.value.details["token"] == "banana"

    def test_rejects_a_non_modifier_in_a_non_final_position(self):
        with pytest.raises(InvalidArguments) as info:
            parse_chord("a+b")
        assert "not a modifier" in str(info.value)

    def test_describe_round_trips(self):
        assert parse_chord("ctrl+shift+s").describe() == "ctrl+shift+s"


class TestParseKeys:
    def test_parses_a_space_separated_string(self):
        chords = parse_keys("ctrl+a delete")
        assert [c.describe() for c in chords] == ["ctrl+a", "delete"]

    def test_parses_a_list(self):
        chords = parse_keys(["ctrl+a", "delete", "enter"])
        assert len(chords) == 3

    def test_a_single_chord_string_is_one_chord(self):
        assert len(parse_keys("ctrl+s")) == 1

    @pytest.mark.parametrize("spec", ["", "   ", []])
    def test_rejects_empty_sequences(self, spec):
        with pytest.raises(InvalidArguments):
            parse_keys(spec)

    def test_rejects_non_string_entries(self):
        with pytest.raises(InvalidArguments):
            parse_keys(["ctrl+s", 7])

    def test_rejects_a_wrong_container_type(self):
        with pytest.raises(InvalidArguments):
            parse_keys({"key": "ctrl+s"})

    def test_one_bad_chord_fails_the_whole_sequence(self):
        # Partially sending a sequence would leave the UI in an unknown state.
        with pytest.raises(InvalidArguments):
            parse_keys(["ctrl+s", "nonsense_key"])

    def test_describe_keys_joins_with_spaces(self):
        assert describe_keys(parse_keys(["ctrl+a", "delete"])) == "ctrl+a delete"
