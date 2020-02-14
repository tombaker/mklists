"""Coerces source_matchpattern to compiled regex (or exits)."""

import re
import pytest
from mklists.rules import Rule

# pylint: disable=anomalous-backslash-in-string
# These are just tests...


def test_compiles_regexstr_correctly():
    """Returns regex string (field 2) in rule object as compiled regex."""
    rule_obj = Rule("1", "NOW", "a.txt", "a.txt", "0")
    actual = rule_obj._coerce_source_matchpattern_as_compiled_regex()
    expected = Rule("1", re.compile("NOW"), "a.txt", "a.txt", "0")
    assert isinstance(rule_obj.source_matchpattern, re.Pattern)
    assert rule_obj.source_matchpattern == re.compile("NOW")
    assert actual == expected


def test_compiles_regexstr_that_was_already_compile():
    """Returns compiled regex given already compiled regex."""
    rule_obj = Rule("1", re.compile("NOW"), "a.txt", "a.txt", "0")
    actual = rule_obj._coerce_source_matchpattern_as_compiled_regex()
    expected = Rule("1", re.compile("NOW"), "a.txt", "a.txt", "0")
    assert isinstance(rule_obj.source_matchpattern, re.Pattern)
    assert rule_obj.source_matchpattern == re.compile("NOW")
    assert actual == expected


def test_compiles_regexstr_with_space():
    """Second field of Rule object, a regex, has an allowable space."""
    rule_obj = Rule(1, "^X 19", "a", "b", 2)
    actual = rule_obj._coerce_source_matchpattern_as_compiled_regex()
    expected = Rule(1, re.compile("^X 19"), "a", "b", 2)
    assert rule_obj.source_matchpattern == re.compile("^X 19")
    assert actual == expected


def test_exits_if_regexstr_has_unescaped_parenthesis():
    """Exits if regex string does not compile(here: unescaped parenthesis)."""
    rule_obj = Rule("1", "N(OW", "a.txt", "a.txt", "0")
    with pytest.raises(SystemExit):
        rule_obj._coerce_source_matchpattern_as_compiled_regex()


def test_compiles_regexstr_with_escaped_parenthesis():
    """Returns compiled regex with escaped parenthesis."""
    rule_obj = Rule(1, "N\(OW", "a", "b", 2)
    actual = rule_obj._coerce_source_matchpattern_as_compiled_regex()
    expected = Rule(1, re.compile("N\\(OW"), "a", "b", 2)
    assert actual == expected


def test_exits_if_regexstr_is_none():
    """Exits if regex string is None."""
    rule_obj = Rule("1", None, "a.txt", "a.txt", "0")
    with pytest.raises(SystemExit):
        rule_obj._coerce_source_matchpattern_as_compiled_regex()


def test_exits_if_regexstr_has_unescaped_backslash():
    """Exits if regex string has unescaped backslash."""
    rule_obj = Rule("1", "N\OW", "a.txt", "a.txt", "0")
    with pytest.raises(SystemExit):
        rule_obj._coerce_source_matchpattern_as_compiled_regex()


def test_exits_if_regexstr_has_escaped_backslash():
    """Raises exception when trying to compile regex with escaped backslash."""
    rule_obj = Rule("1", "N\\OW", "a.txt", "a.txt", "0")
    with pytest.raises(SystemExit):
        rule_obj._coerce_source_matchpattern_as_compiled_regex()


def test_compiles_regexstr_with_double_escaped_backslash():
    """Compiles regex string with double-escaped backslash."""
    rule_obj = Rule(1, "N\\\\OW", "a", "b", 2)
    actual = rule_obj._coerce_source_matchpattern_as_compiled_regex()
    expected = Rule(1, re.compile("N\\\\OW"), "a", "b", 2)
    assert actual == expected


def test_compiles_regexstr_with_backslash_chain():
    """Returns compiled regex from string with backslash chain."""
    rule_obj = Rule(1, "\d\d\d", "a", "b", 2)
    actual = rule_obj._coerce_source_matchpattern_as_compiled_regex()
    expected = Rule(1, re.compile("\\d\\d\\d"), "a", "b", 2)
    assert actual == expected


def test_compile_regex_with_phone_number_regex():
    """Returns compiled regex from regex for a US telephone number."""
    rule_obj = Rule(1, "^(\d{3})-(\d{3})-(\d{4})$", "a", "b", 2)
    actual = rule_obj._coerce_source_matchpattern_as_compiled_regex()
    expected = Rule(1, re.compile("^(\\d{3})-(\\d{3})-(\\d{4})$"), "a", "b", 2)
    assert actual == expected
    assert re.search(expected.source_matchpattern, "216-321-1234")


def test_compiles_regexstr_with_uppercase_letters_only():
    """Returns compiled regex from regex with uppercase characters."""
    rule_obj = Rule(1, "^[A-Z]*$", "a", "b", 2)
    actual = rule_obj._coerce_source_matchpattern_as_compiled_regex()
    expected = Rule(1, re.compile("^[A-Z]*$"), "a", "b", 2)
    assert actual == expected
    assert re.search(expected.source_matchpattern, "ASDF")


def test_compiles_regexstr_with_wildcards_and_one_space():
    """Returns compiled regex from regex with uppercase characters."""
    rule_obj = Rule(1, "^=* ", "a", "b", 2)
    actual = rule_obj._coerce_source_matchpattern_as_compiled_regex()
    expected = Rule(1, re.compile("^=* "), "a", "b", 2)
    assert actual == expected
    assert re.search(expected.source_matchpattern, "= ")
    assert re.search(expected.source_matchpattern, "== ")
    assert re.search(expected.source_matchpattern, "====== ")
