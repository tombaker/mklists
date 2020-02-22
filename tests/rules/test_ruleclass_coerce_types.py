"""Coerces fields of data class to specific types (or exits with error)."""

import re
import pytest
from pathlib import Path
from mklists.rules import Rule


def test_pathlike_object_is_valid_filename():
    """Source could be a Path object."""
    rule_obj = Rule(1, "NOW", Path("a"), "b", 2)
    rule_obj.coerce_types()
    assert rule_obj.source == "a"


def test_raise_exception_given_bad_filename_string():
    """Source (filename) must not contain invalid characters."""
    rule_obj = Rule(1, "NOW", "a/2:", "b", 2)
    with pytest.raises(SystemExit):
        rule_obj.coerce_types()


def test_raise_exception_given_source_filename_none():
    """Source (filename) must not be None."""
    rule_obj = Rule(1, "NOW", None, "b", 2)
    with pytest.raises(SystemExit):
        rule_obj.coerce_types()


def test_coerce_types_given_good_string():
    """Source matchfield must be an integer."""
    rule_obj = Rule("1", "NOW", "a", "b", 2)
    rule_obj.coerce_types()
    assert isinstance(rule_obj.source_matchfield, int)
    assert rule_obj.source_matchfield == 1


def test_returns_compiled_regex_given_already_compiled_regex():
    """Returns compiled regex given already compiled regex."""
    rule_obj = Rule("1", re.compile("NOW"), "a.txt", "a.txt", "0")
    actual = rule_obj.coerce_types()
    expected = Rule(1, re.compile("NOW"), "a.txt", "a.txt", 0)
    assert isinstance(rule_obj.source_matchpattern, re.Pattern)
    assert rule_obj.source_matchpattern == re.compile("NOW")
    assert actual == expected


def test_compiles_regexstr_with_space():
    """Second field of Rule object, a regex, has an allowable space."""
    rule_obj = Rule(1, "^X 19", "a", "b", 2)
    actual = rule_obj.coerce_types()
    expected = Rule(1, re.compile("^X 19"), "a", "b", 2)
    assert rule_obj.source_matchpattern == re.compile("^X 19")
    assert actual == expected


def test_exits_if_regexstr_has_unescaped_parenthesis():
    """Exits if regex string does not compile(here: unescaped parenthesis)."""
    rule_obj = Rule("1", "N(OW", "a.txt", "a.txt", "0")
    with pytest.raises(SystemExit):
        rule_obj.coerce_types()


def test_compiles_regexstr_with_double_escaped_backslash():
    """Compiles regex string with double-escaped backslash."""
    rule_obj = Rule(1, "N\\\\OW", "a", "b", 2)
    actual = rule_obj.coerce_types()
    expected = Rule(1, re.compile("N\\\\OW"), "a", "b", 2)
    assert actual == expected


def test_compiles_regexstr_with_uppercase_letters_only():
    """Returns compiled regex from regex with uppercase characters."""
    rule_obj = Rule(1, "^[A-Z]*$", "a", "b", 2)
    actual = rule_obj.coerce_types()
    expected = Rule(1, re.compile("^[A-Z]*$"), "a", "b", 2)
    assert actual == expected
    assert re.search(expected.source_matchpattern, "ASDF")


def test_coerce_target_sortorder_as_integer_raise_exception_given_bad_string():
    """Target sortorder must be an integer."""
    rule_obj = Rule("1 2", "NOW", "a", "b", "1 2")
    with pytest.raises(SystemExit):
        rule_obj.coerce_types()


def test_coerce_target_sortorder_as_integer_raise_exception_given_non_integer():
    """Perversely, int(1.2) evaluates to 1; improbable edge case?"""
    rule_obj = Rule(1.2, "NOW", "a", "b", 1.2)
    rule_obj.coerce_types()
    assert isinstance(rule_obj.target_sortorder, int)
    assert rule_obj.target_sortorder == 1
