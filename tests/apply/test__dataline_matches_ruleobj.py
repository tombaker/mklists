"""Returns True if line (or part of line) matches a given regular expression."""

from mklists.apply import _dataline_matches_ruleobj
from mklists.rules import Rule


def test_match():
    """Match, simple regex in field 1."""
    rule = Rule(1, "NOW", "a.txt", "b.txt", 0)
    line = "NOW Buy milk"
    assert _dataline_matches_ruleobj(ruleobj=rule, dataline_str=line)


def test_no_match():
    """No match to simple regex in field 1."""
    rule = Rule(1, "NOW", "a.txt", "b.txt", 0)
    line = "LATER Buy milk"
    assert not _dataline_matches_ruleobj(ruleobj=rule, dataline_str=line)


def test_match_despite_leading_whitespace():
    """Returns True: matches regex in field 1, despite leading whitespace."""
    rule = Rule(1, "NOW", "a.txt", "b.txt", 0)
    line = " NOW Buy milk"
    assert _dataline_matches_ruleobj(ruleobj=rule, dataline_str=line)


def test_match_despite_leading_whitespace_with_caret():
    """Match, despite leading whitespace, which is ignored."""
    rule = Rule(1, "^NOW", "a.txt", "b.txt", 0)
    line = " NOW Buy milk"
    assert _dataline_matches_ruleobj(ruleobj=rule, dataline_str=line)


def test_match_start_of_entire_line():
    """Match, because regex matches start of the entire line."""
    rule = Rule(0, "^NOW", "a.txt", "b.txt", 0)
    line = "NOW Buy milk"
    assert _dataline_matches_ruleobj(ruleobj=rule, dataline_str=line)


def test_match_when_parenthesis_properly_escaped():
    """Match, because open paren is properly escaped."""
    # pylint: disable=anomalous-backslash-in-string
    # Thank you for catching this, Pylint, but the mistake is intentional...
    rule = Rule(0, "^N\(OW", "a.txt", "b.txt", 0)
    assert _dataline_matches_ruleobj(ruleobj=rule, dataline_str="N(OW Buy milk")


def test_no_match_when_line_has_less_fields_than_source_matchfield():
    """Returns False because line does not have six fields."""
    rule = Rule(6, "^NOW", "a.txt", "b.txt", 0)
    line = "NOW Buy milk"
    assert not _dataline_matches_ruleobj(ruleobj=rule, dataline_str=line)
