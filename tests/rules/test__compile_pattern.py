"""Tests ~/github/tombaker/mklists/src/mklists/rules.py

House rule: All regex literals must be raw strings.
Documentation should make this clear.
"""

# pylint: disable=anomalous-backslash-in-string

import re
import pytest
from mklists.rules import _compile_pattern, Rule, RuleError


def test_valid_regex_returns_compiled_pattern():
    """Valid regex returns compiled pattern."""
    pattern = _compile_pattern(r"^[A-Z]+[0-9]*$")

    assert isinstance(pattern, re.Pattern)
    assert pattern.pattern == r"^[A-Z]+[0-9]*$"


def test_empty_string_is_valid_regex():
    """Empty string is a valid regex; should it really be valid for mklists?"""
    pattern = _compile_pattern("")

    assert isinstance(pattern, re.Pattern)
    assert pattern.pattern == ""


def test_invalid_regex_raises_rule_validation_error():
    """Invalid regex text (here: unescaped parenthesis) raises RuleError."""
    with pytest.raises(RuleError):
        _compile_pattern("(")


def test_error_message_includes_original_pattern():
    """Error message for RuleError includes text of bad regex text."""
    bad_pattern = "("
    with pytest.raises(RuleError) as excinfo:
        _compile_pattern(bad_pattern)

    message = str(excinfo.value)
    assert bad_pattern in message


def test_original_re_error_is_chained():
    """Python keeps reference to original exception as cause of new exception."""
    try:
        _compile_pattern("(")
    except RuleError as exc:
        assert exc.__cause__ is not None
        assert isinstance(exc.__cause__, re.error)


def test_compiles_regexstr_with_space():
    """Regex text has an allowable space."""
    pattern = _compile_pattern("^X 19")

    assert isinstance(pattern, re.Pattern)
    assert pattern.pattern == "^X 19"


def test_compiles_regexstr_with_double_escaped_backslash():
    """Compiles regex string with double-escaped backslash. Use raw strings!"""
    pattern = _compile_pattern("N\\\\OW")
    pattern_raw = _compile_pattern(r"N\\OW")

    assert isinstance(pattern, re.Pattern)
    assert isinstance(pattern_raw, re.Pattern)
    assert pattern.pattern == "N\\\\OW"
    assert pattern_raw.pattern == r"N\\OW"


def test_compiles_regexstr_with_raw_string_escaped_parenthesis():
    """Returns compiled regex with escaped parenthesis if passed as "raw"."""
    pattern = _compile_pattern(r"N\(OW")

    assert isinstance(pattern, re.Pattern)
    assert pattern.pattern == r"N\(OW"


def test_compile_regex_with_phone_number_regex():
    """Returns compiled regex from regex for a US telephone number."""
    pattern = _compile_pattern(r"^(\d{3})-(\d{3})-(\d{4})$")

    assert isinstance(pattern, re.Pattern)
    assert pattern == re.compile("^(\\d{3})-(\\d{3})-(\\d{4})$")
    assert re.match(pattern, "216-321-1234")


def test_compiles_regexstr_with_wildcards_and_one_space():
    """Returns compiled regex from regex with uppercase characters."""
    pattern = _compile_pattern(r"^=* ")

    assert isinstance(pattern, re.Pattern)
    assert re.search(pattern, "= ")
    assert re.search(pattern, "== ")
    assert re.search(pattern, "====== ")
