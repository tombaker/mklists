"""Tests $MKLMKL/rules/resolve.py"""

import re
import pytest
from mklists.errors import RuleError
from mklists.rules.model import Rule, SortKey
from mklists.rules.load import _parse_rule


def test_valid_rule_is_parsed_correctly():
    """Valid rule is parsed correctly."""
    ruleline_fields = ["2", "^abc$", "source", "target", "5"]
    rule = _parse_rule(ruleline_fields)
    assert isinstance(rule, Rule)
    assert rule.source_matchfield == 2
    assert isinstance(rule.source_matchpattern, re.Pattern)
    assert rule.source_matchpattern.pattern == "^abc$"
    assert rule.source == "source"
    assert rule.target == "target"
    assert rule.target_sortkeys == [SortKey(field=5)]


def test_source_and_target_are_stripped():
    """Source and target are stripped of whitespace on left and right."""
    ruleline_fields = ["1", ".*", "  source  ", "  target  ", "1"]
    rule = _parse_rule(ruleline_fields)
    assert rule.source == "source"
    assert rule.target == "target"


def test_negative_source_matchfield_raises_rule_error():
    """Negative source matchfield raises RuleError."""
    ruleline_fields = ["-1", ".*", "source", "target", "1"]
    with pytest.raises(RuleError):
        _parse_rule(ruleline_fields)


def test_non_integer_source_matchfield_raises_rule_validation_error():
    """Non-integer source matchfield raises RuleError."""
    ruleline_fields = ["x", ".*", "source", "target", "1"]
    with pytest.raises(RuleError):
        _parse_rule(ruleline_fields)


def test_invalid_target_sortkey_raises_rule_validation_error():
    """Sort spec with no leading digits raises RuleError."""
    ruleline_fields = ["1", ".*", "source", "target", "x"]
    with pytest.raises(RuleError):
        _parse_rule(ruleline_fields)


def test_invalid_regex_raises_rule_validation_error():
    """Invalid regex in source match pattern raises RuleError."""
    ruleline_fields = ["1", "(", "source", "target", "1"]
    with pytest.raises(RuleError):
        _parse_rule(ruleline_fields)


def test_source_equal_to_target_after_stripping_raises_rule_validation_error():
    """Source equal to target (after stripping) raises RuleError."""
    ruleline_fields = ["1", ".*", " same ", "same", "1"]
    with pytest.raises(RuleError):
        _parse_rule(ruleline_fields)


@pytest.mark.parametrize(
    "with_empty_field",
    [
        ["", ".*", "source", "target", "1"],
        ["1", "", "source", "target", "1"],
        ["1", ".*", "   ", "target", "1"],
        ["1", ".*", "source", "   ", "1"],
    ],
)
def test_empty_source_matchfield_raises_format_error(with_empty_field):
    """If required field is empty, raises RuleError."""
    with pytest.raises(RuleError):
        _parse_rule(with_empty_field)


@pytest.mark.parametrize(
    "bad_sortorder",
    ["-1", "1.1"],
)
def test_invalid_sort_spec_format_raises_error(bad_sortorder):
    """Sort specs with a leading minus or decimal point raise RuleError."""
    ruleline_fields = ["1", ".*", "source", "target", bad_sortorder]
    with pytest.raises(RuleError):
        _parse_rule(ruleline_fields)


def test_blank_sortorder_gives_none():
    """Blank fifth field yields target_sortkeys of None."""
    ruleline_fields = ["1", ".*", "source", "target", ""]
    rule = _parse_rule(ruleline_fields)
    assert rule.target_sortkeys is None


def test_multikey_sortorder_is_parsed():
    """Comma-separated sort specs produce a list of SortKey objects."""
    ruleline_fields = ["1", ".*", "source", "target", "1,3"]
    rule = _parse_rule(ruleline_fields)
    assert rule.target_sortkeys == [SortKey(field=1), SortKey(field=3)]


def test_sort_modifiers_are_parsed():
    """Modifiers r, n, f are parsed onto each SortKey."""
    ruleline_fields = ["1", ".*", "source", "target", "1r,3n,2f"]
    rule = _parse_rule(ruleline_fields)
    assert rule.target_sortkeys == [
        SortKey(field=1, reverse=True),
        SortKey(field=3, numeric=True),
        SortKey(field=2, casefold=True),
    ]


def test_combined_modifiers_on_one_key():
    """Multiple modifiers may appear on a single sort spec."""
    ruleline_fields = ["1", ".*", "source", "target", "2rn"]
    rule = _parse_rule(ruleline_fields)
    assert rule.target_sortkeys == [SortKey(field=2, reverse=True, numeric=True)]
