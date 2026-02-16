"""Tests ~/github/tombaker/mklists/src/mklists/rules.py"""

import re
import pytest
from mklists.rules import (
    _parse_rule,
    Rule,
    RuleError,
)


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
    assert rule.target_sortkey == 5


def test_source_and_target_are_stripped():
    """Source and target are stripped of whitespace on left and right."""
    ruleline_fields = ["1", ".*", "  source  ", "  target  ", "1"]
    rule = _parse_rule(ruleline_fields)
    assert rule.source == "source"
    assert rule.target == "target"


def test_non_integer_source_matchfield_raises_rule_validation_error():
    """Non-integer source matchfield raises RuleError."""
    ruleline_fields = ["x", ".*", "source", "target", "1"]
    with pytest.raises(RuleError):
        _parse_rule(ruleline_fields)


def test_non_integer_target_sortkey_raises_rule_validation_error():
    """Non-integer target sort order raises RuleError."""
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
def test_target_sortkey_less_than_zero_raises_error(bad_sortorder):
    """Target sort order must be a greater than zero."""
    ruleline_fields = ["1", ".*", "source", "target", bad_sortorder]
    with pytest.raises(RuleError):
        _parse_rule(ruleline_fields)
