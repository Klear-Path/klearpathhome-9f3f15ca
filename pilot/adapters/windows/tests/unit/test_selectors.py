"""Semantic selector matching and ranking."""

from __future__ import annotations

import pytest

from ...errors import AmbiguousSelector, ElementNotFound, InvalidArguments
from ...model import PATTERN_INVOKE, PATTERN_VALUE, ElementSnapshot, Rect
from ...control_selectors import MatchMode, Selector, find_all, resolve_one


def element(**kwargs) -> ElementSnapshot:
    kwargs.setdefault("runtime_id", kwargs.get("name", "e"))
    return ElementSnapshot(**kwargs)


@pytest.fixture
def dialog() -> ElementSnapshot:
    """A dialog with the awkward shapes real UI actually has."""
    ok_button = element(runtime_id="ok", name="OK", role="Button",
                        automation_id="btnOk", class_name="Button",
                        patterns=(PATTERN_INVOKE,), keyboard_focusable=True,
                        depth=2, rect=Rect(0, 0, 80, 24))
    cancel = element(runtime_id="cancel", name="Cancel", role="Button",
                     automation_id="btnCancel", patterns=(PATTERN_INVOKE,),
                     keyboard_focusable=True, depth=2)
    disabled_apply = element(runtime_id="apply", name="Apply", role="Button",
                             automation_id="btnApply", enabled=False,
                             patterns=(PATTERN_INVOKE,), depth=2)
    hidden_help = element(runtime_id="help", name="Help", role="Button",
                          offscreen=True, patterns=(PATTERN_INVOKE,), depth=2)
    name_label = element(runtime_id="lbl", name="File name:", role="Text", depth=2)
    name_edit = element(runtime_id="edit", name="File name:", role="Edit",
                        automation_id="1001", value="report.txt",
                        patterns=(PATTERN_VALUE,), keyboard_focusable=True, depth=2)
    custom = element(runtime_id="custom", name="", role="Custom",
                     class_name="DirectUIHWND", depth=2)
    group = element(runtime_id="group", role="Group", depth=1,
                    children=(name_label, name_edit, ok_button, cancel,
                              disabled_apply, hidden_help, custom))
    return element(runtime_id="root", name="Save As", role="Window", depth=0,
                   children=(group,))


class TestSelectorConstruction:
    def test_requires_at_least_one_criterion(self):
        with pytest.raises(InvalidArguments):
            Selector()

    def test_normalises_the_role(self):
        assert Selector(role="ButtonControl").role == "button"

    def test_rejects_an_unknown_match_mode(self):
        with pytest.raises(InvalidArguments):
            Selector(name="x", name_match="fuzzy")

    def test_rejects_a_negative_index(self):
        with pytest.raises(InvalidArguments):
            Selector(role="button", index=-1)

    def test_from_mapping_accepts_control_type_as_a_role_alias(self):
        assert Selector.from_mapping({"control_type": "Button"}).role == "button"

    def test_from_mapping_wraps_a_bare_pattern_string(self):
        assert Selector.from_mapping({"requires_patterns": "value"}).requires_patterns == ("value",)

    def test_from_mapping_rejects_unknown_keys(self):
        # A typo'd key must not silently widen the search.
        with pytest.raises(InvalidArguments) as info:
            Selector.from_mapping({"nmae": "OK"})
        assert "nmae" in info.value.details["unknown_keys"]

    @pytest.mark.parametrize("raw", [None, {}, ""])
    def test_from_mapping_rejects_empty_input(self, raw):
        with pytest.raises(InvalidArguments):
            Selector.from_mapping(raw)

    def test_from_mapping_rejects_a_non_mapping(self):
        with pytest.raises(InvalidArguments):
            Selector.from_mapping(["OK"])

    def test_from_mapping_passes_through_a_selector(self):
        original = Selector(name="OK")
        assert Selector.from_mapping(original) is original


class TestTextMatching:
    @pytest.mark.parametrize("mode,needle,should_match", [
        (MatchMode.EXACT, "OK", True),
        (MatchMode.EXACT, "ok", False),
        (MatchMode.IEQUALS, "ok", True),
        (MatchMode.IEQUALS, "o", False),
        (MatchMode.CONTAINS, "K", True),
        (MatchMode.STARTSWITH, "o", True),
        (MatchMode.STARTSWITH, "K", False),
        (MatchMode.REGEX, r"^O.$", True),
        (MatchMode.REGEX, r"^X", False),
    ])
    def test_name_modes(self, dialog, mode, needle, should_match):
        found = find_all(dialog, Selector(name=needle, name_match=mode, role="button"))
        assert any(m.element.runtime_id == "ok" for m in found) is should_match

    def test_invalid_regex_is_reported_structurally(self):
        with pytest.raises(InvalidArguments):
            find_all(element(runtime_id="x", name="a"),
                     Selector(name="[unclosed", name_match=MatchMode.REGEX))


class TestFiltering:
    def test_disabled_elements_are_excluded_by_default(self, dialog):
        assert find_all(dialog, Selector(name="Apply")) == []

    def test_disabled_elements_can_be_included(self, dialog):
        found = find_all(dialog, Selector(name="Apply", enabled_only=False))
        assert [m.element.runtime_id for m in found] == ["apply"]

    def test_offscreen_elements_are_excluded_by_default(self, dialog):
        assert find_all(dialog, Selector(name="Help")) == []

    def test_focusable_only_filters_non_focusable(self, dialog):
        found = find_all(dialog, Selector(name="File name:", focusable_only=True))
        assert [m.element.runtime_id for m in found] == ["edit"]

    def test_automation_id_is_an_exact_match(self, dialog):
        found = find_all(dialog, Selector(automation_id="btnOk"))
        assert [m.element.runtime_id for m in found] == ["ok"]

    def test_class_name_filters(self, dialog):
        found = find_all(dialog, Selector(class_name="DirectUIHWND"))
        assert [m.element.runtime_id for m in found] == ["custom"]

    def test_required_patterns_filter(self, dialog):
        found = find_all(dialog, Selector(role="edit", requires_patterns=(PATTERN_VALUE,)))
        assert [m.element.runtime_id for m in found] == ["edit"]

    def test_required_patterns_exclude_pattern_less_elements(self, dialog):
        assert find_all(dialog, Selector(role="custom",
                                        requires_patterns=(PATTERN_INVOKE,))) == []

    def test_value_matching(self, dialog):
        found = find_all(dialog, Selector(value="report"))
        assert [m.element.runtime_id for m in found] == ["edit"]

    def test_max_depth_prunes(self, dialog):
        assert find_all(dialog, Selector(role="button", max_depth=1)) == []

    def test_criteria_are_anded(self, dialog):
        # 'File name:' matches two elements; adding the role picks exactly one.
        assert len(find_all(dialog, Selector(name="File name:"))) == 2
        assert len(find_all(dialog, Selector(name="File name:", role="edit"))) == 1


class TestRanking:
    def test_exact_name_outranks_a_contains_match(self):
        exact = element(runtime_id="exact", name="Save", role="Button", depth=1)
        loose = element(runtime_id="loose", name="Save As...", role="Button", depth=1)
        root = element(runtime_id="root", role="Window", children=(loose, exact))
        found = find_all(root, Selector(name="Save", name_match=MatchMode.CONTAINS,
                                        role="button"))
        assert found[0].element.runtime_id == "exact"

    def test_shallower_elements_win_ties(self):
        deep = element(runtime_id="deep", name="Go", role="Button", depth=5)
        shallow_child = element(runtime_id="shallow", name="Go", role="Button", depth=1)
        root = element(runtime_id="root", role="Window",
                       children=(element(runtime_id="mid", role="Group", depth=1,
                                         children=(deep,)), shallow_child))
        found = find_all(root, Selector(name="Go", role="button"))
        assert found[0].element.runtime_id == "shallow"

    def test_results_are_deterministic_across_repeated_calls(self, dialog):
        selector = Selector(role="button")
        first = [m.element.runtime_id for m in find_all(dialog, selector)]
        for _ in range(5):
            assert [m.element.runtime_id for m in find_all(dialog, selector)] == first

    def test_index_mode_orders_by_document_position(self, dialog):
        ordered = [m.element.runtime_id for m in
                   find_all(dialog, Selector(role="button", index=0))]
        assert ordered == ["ok", "cancel"]


class TestResolveOne:
    def test_returns_the_best_match(self, dialog):
        assert resolve_one(dialog, Selector(automation_id="btnOk")).runtime_id == "ok"

    def test_raises_element_not_found_with_diagnostics(self, dialog):
        with pytest.raises(ElementNotFound) as info:
            resolve_one(dialog, Selector(name="Nonexistent"))
        assert info.value.retryable is True
        assert info.value.details["searched_elements"] > 0

    def test_near_misses_explain_a_disabled_control(self, dialog):
        # "found but disabled" and "no such control" need different recovery.
        with pytest.raises(ElementNotFound) as info:
            resolve_one(dialog, Selector(name="Apply"))
        reasons = [r for m in info.value.details["near_misses"] for r in m["reasons"]]
        assert "disabled" in reasons

    def test_near_misses_explain_a_wrong_role(self, dialog):
        with pytest.raises(ElementNotFound) as info:
            resolve_one(dialog, Selector(name="Cancel", role="edit"))
        reasons = " ".join(r for m in info.value.details["near_misses"]
                           for r in m["reasons"])
        assert "role is" in reasons

    def test_require_unique_raises_on_a_genuine_tie(self):
        a = element(runtime_id="a", name="Item", role="Button", depth=1)
        b = element(runtime_id="b", name="Item", role="Button", depth=1)
        root = element(runtime_id="root", role="Window", children=(a, b))
        with pytest.raises(AmbiguousSelector) as info:
            resolve_one(root, Selector(name="Item", role="button"), require_unique=True)
        assert len(info.value.details["candidates"]) == 2
        assert info.value.retryable is False

    def test_require_unique_accepts_a_clear_winner(self, dialog):
        assert resolve_one(dialog, Selector(name="OK", role="button"),
                           require_unique=True).runtime_id == "ok"

    def test_index_selects_the_nth_match(self, dialog):
        assert resolve_one(dialog, Selector(role="button", index=1)).runtime_id == "cancel"

    def test_index_out_of_range_raises(self, dialog):
        with pytest.raises(ElementNotFound) as info:
            resolve_one(dialog, Selector(role="button", index=99))
        assert info.value.details["match_count"] == 2
