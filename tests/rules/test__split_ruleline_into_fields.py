"""Tests $MKLMKL/rules/resolve.py"""

import pytest
from mklists.errors import RuleError
from mklists.rules.load import _split_ruleline_into_fields, PIPE, FIELD_COUNT


def test_valid_ruleline_is_split_into_fields():
    """Trivial list is valid with five text fields."""
    rule_line = PIPE.join(str(i) for i in range(FIELD_COUNT))
    ruleline_fields = _split_ruleline_into_fields(rule_line)
    assert len(ruleline_fields) == FIELD_COUNT
    assert ruleline_fields == ["0", "1", "2", "3", "4"]


def test_trailing_empty_field_is_preserved():
    """Trailing empty field is preserved."""
    rule_line = "0|.|lines|__RENAME__|"
    ruleline_fields = _split_ruleline_into_fields(rule_line)
    assert len(ruleline_fields) == FIELD_COUNT
    assert ruleline_fields == ["0", ".", "lines", "__RENAME__", ""]


def test_too_few_fields_raises_rule_format_error():
    """Raises RuleError if too few fields."""
    rule_line = PIPE.join(["a", "b", "c"])
    with pytest.raises(RuleError):
        _split_ruleline_into_fields(rule_line)


def test_too_many_fields_raises_rule_format_error():
    """Raises RuleError if too many fields."""
    rule_line = PIPE.join(str(i) for i in range(FIELD_COUNT + 1))
    with pytest.raises(RuleError):
        _split_ruleline_into_fields(rule_line)


def test_error_message_includes_original_line():
    """Error message includes original line."""
    rule_line = "a|b|c"
    with pytest.raises(RuleError) as excinfo:
        _split_ruleline_into_fields(rule_line)

    message = str(excinfo.value)
    assert rule_line in message
