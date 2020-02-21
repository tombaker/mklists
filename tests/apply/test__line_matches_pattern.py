"""Returns True if line (or part of line) matches a given regular expression."""

from mklists.apply import _line_matches_pattern


def test_match():
    """Match simple regex in field 1."""
    pattern = "NOW"
    field_int = 1
    line = "NOW Buy milk"
    assert _line_matches_pattern(pattern, field_int, line)


def test_no_match():
    """No match to simple regex in field 1."""
    pattern = "NOW"
    field_int = 1
    line = "LATER Buy milk"
    assert not _line_matches_pattern(pattern, field_int, line)


def test_match_despite_leading_whitespace():
    """Match, despite leading whitespace."""
    pattern = "NOW"
    field_int = 1
    line = " NOW Buy milk"
    assert _line_matches_pattern(pattern, field_int, line)


def test_match_despite_leading_whitespace_with_caret():
    """Match, despite leading whitespace, which is lost to .split()."""
    pattern = "^NOW"
    field_int = 1
    line = " NOW Buy milk"
    assert _line_matches_pattern(pattern, field_int, line)


def test_match_start_of_entire_line():
    """Match, because regex matches start of entire line."""
    pattern = "^NOW"
    field_int = 0
    line = "NOW Buy milk"
    assert _line_matches_pattern(pattern, field_int, line)


def test_match_when_parenthesis_properly_escaped():
    """Match, because open paren is properly escaped."""
    # pylint: disable=anomalous-backslash-in-string
    pattern = "^N\(OW"
    field_int = 0
    line = "N(OW Buy milk"
    assert _line_matches_pattern(pattern, field_int, line)


def test_no_match_when_line_has_less_fields_than_source_matchfield():
    """No match, because line has less than six fields."""
    pattern = "^NOW"
    field_int = 6
    line = "NOW Buy milk"
    assert not _line_matches_pattern(pattern, field_int, line)
