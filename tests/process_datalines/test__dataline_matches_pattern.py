"""@@@"""

import re
import pytest
from mklists.process_datalines import _dataline_matches_pattern


def test_dataline_matches_pattern_returns_false_when_field_exists_but_no_match():
    """Minimal pytest to reach 'return False': field exists but does not match.

    Note:
    - `re.search(re.compile("delta"), "beta")` returns None.
    - Execution reaches the final `return False`.
    """
    dataline = "alpha beta gamma\n"
    pattern = re.compile(r"delta")

    result = _dataline_matches_pattern(
        dataline=dataline,
        pattern=pattern,
        onebased_matchfield=2,  # "beta"
    )

    assert result is False


def test_dataline_matches_pattern_true_when_regex_matches_existing_field():
    """Returns True when regex matches existing field.

    Note:
    - `re.search(re.compile("bet"), "beta")` returns truthy
      <re.Match object; span=(0, 3), match='bet'>
    """
    dataline = "alpha beta gamma\n"
    pattern = re.compile(r"bet")

    assert _dataline_matches_pattern(dataline, pattern, 2) is True


def test_dataline_matches_pattern_false_for_negative_matchfield():
    """Returns False if matchfield is a negative integer."""
    dataline = "alpha beta\n"
    pattern = re.compile(r"alpha")

    assert _dataline_matches_pattern(dataline, pattern, -1) is False


def test_dataline_matches_pattern_true_for_whole_line_match():
    """Returns True if whole-line match succeeds."""
    dataline = "alpha beta gamma\n"
    pattern = re.compile(r"beta")

    assert _dataline_matches_pattern(dataline, pattern, 0) is True


def test_dataline_matches_pattern_false_for_whole_line_no_match():
    """Returns False if whole-line match fails."""
    dataline = "alpha beta gamma\n"
    pattern = re.compile(r"delta")

    assert _dataline_matches_pattern(dataline, pattern, 0) is False


def test_dataline_matches_pattern_false_when_field_does_not_exist():
    """Returns False if field to be matched does not exist (ie, not enough fields)."""
    dataline = "alpha beta\n"
    pattern = re.compile(r"beta")

    assert _dataline_matches_pattern(dataline, pattern, 3) is False


def test_dataline_matches_pattern_empty_line():
    """Returns False when dataline is 'empty'."""
    dataline = "\n"
    pattern = re.compile(r".+")

    assert _dataline_matches_pattern(dataline, pattern, 0) is False
    assert _dataline_matches_pattern(dataline, pattern, 1) is False
