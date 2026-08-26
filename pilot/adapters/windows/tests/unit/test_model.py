"""Snapshot model and role normalisation."""

from __future__ import annotations

import pytest

from ...model import (
    PATTERN_INVOKE, PATTERN_VALUE,
    ElementSnapshot, Rect, WindowInfo,
    describe_tree_stats, flatten, normalize_role, summarize_tree,
)


class TestRect:
    def test_dimensions(self):
        rect = Rect(10, 20, 110, 70)
        assert (rect.width, rect.height) == (100, 50)

    def test_center(self):
        assert Rect(0, 0, 100, 50).center == (50, 25)

    @pytest.mark.parametrize("rect", [Rect(), Rect(10, 10, 10, 20), Rect(10, 10, 20, 10)])
    def test_degenerate_rects_are_empty(self, rect):
        assert rect.is_empty

    def test_inverted_rect_clamps_to_zero(self):
        assert Rect(100, 100, 0, 0).width == 0


class TestNormalizeRole:
    @pytest.mark.parametrize("raw,expected", [
        ("Button", "button"),
        ("button", "button"),
        ("ButtonControl", "button"),
        ("ControlType.Button", "button"),
        ("Edit", "edit"),
        ("TextBox", "edit"),
        ("MenuItem", "menu_item"),
        ("menu item", "menu_item"),
        ("Document", "document"),
        ("CheckBox", "check_box"),
        ("Dialog", "window"),
        ("Hyperlink", "hyperlink"),
        ("Link", "hyperlink"),
    ])
    def test_folds_known_spellings(self, raw, expected):
        assert normalize_role(raw) == expected

    @pytest.mark.parametrize("raw", [None, "", "   "])
    def test_empty_roles_become_empty_string(self, raw):
        assert normalize_role(raw) == ""

    def test_unknown_role_passes_through_lowercased(self):
        # Providers invent control types; describing one imperfectly beats
        # refusing to represent it.
        assert normalize_role("QuantumWidget") == "quantumwidget"


def _tree() -> ElementSnapshot:
    leaf_a = ElementSnapshot(runtime_id="a", name="Save", role="Button",
                             patterns=(PATTERN_INVOKE,), depth=2)
    leaf_b = ElementSnapshot(runtime_id="b", name="Cancel", role="Button",
                             patterns=(PATTERN_INVOKE,), depth=2, enabled=False)
    leaf_c = ElementSnapshot(runtime_id="c", name="", role="Custom", depth=2)
    group = ElementSnapshot(runtime_id="g", role="Group", depth=1,
                            children=(leaf_a, leaf_b, leaf_c))
    return ElementSnapshot(runtime_id="root", name="Dialog", role="Window",
                           depth=0, children=(group,))


class TestElementSnapshot:
    def test_role_is_normalised_on_construction(self):
        assert ElementSnapshot(runtime_id="x", role="ButtonControl").role == "button"

    def test_walk_is_depth_first_and_includes_self(self):
        assert [n.runtime_id for n in _tree().walk()] == ["root", "g", "a", "b", "c"]

    def test_interactable_requires_enabled_and_onscreen(self):
        assert ElementSnapshot(runtime_id="x").interactable
        assert not ElementSnapshot(runtime_id="x", enabled=False).interactable
        assert not ElementSnapshot(runtime_id="x", offscreen=True).interactable

    def test_supports_checks_the_pattern_list(self):
        element = ElementSnapshot(runtime_id="x", patterns=(PATTERN_VALUE,))
        assert element.supports(PATTERN_VALUE)
        assert not element.supports(PATTERN_INVOKE)

    def test_to_dict_can_omit_children(self):
        assert "children" not in _tree().to_dict(include_children=False)
        assert "children" in _tree().to_dict()

    def test_describe_mentions_salient_attributes(self):
        text = ElementSnapshot(runtime_id="x", name="Save", role="Button",
                               automation_id="btnSave", enabled=False).describe()
        assert "button" in text and "Save" in text
        assert "btnSave" in text and "disabled" in text


class TestTreeHelpers:
    def test_flatten_preserves_document_order(self):
        assert [n.runtime_id for n in flatten(_tree())] == ["root", "g", "a", "b", "c"]

    def test_flatten_prunes_below_max_depth(self):
        assert [n.runtime_id for n in flatten(_tree(), max_depth=1)] == ["root", "g"]

    def test_summarize_tree_respects_the_limit(self):
        assert len(summarize_tree(_tree(), limit=2)) == 2

    def test_stats_count_elements_and_roles(self):
        stats = describe_tree_stats(_tree())
        assert stats["total_elements"] == 5
        assert stats["max_depth"] == 2
        assert stats["roles"]["button"] == 2

    def test_stats_count_only_usable_interactables(self):
        # 'a' is enabled with a pattern; 'b' is disabled; 'c' has no pattern.
        assert describe_tree_stats(_tree())["interactable_elements"] == 1

    def test_stats_count_named_elements(self):
        assert describe_tree_stats(_tree())["named_elements"] == 3


class TestWindowInfo:
    def test_to_dict_nests_the_rect(self):
        payload = WindowInfo(handle=1, title="T", rect=Rect(0, 0, 10, 10)).to_dict()
        assert payload["rect"]["right"] == 10
        assert payload["title"] == "T"
