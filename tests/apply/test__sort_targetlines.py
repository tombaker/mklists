"""@@@Docstring"""

from mklists.apply import _dsusort_lines


def test_lines_not_sorted_if_sortorder_is_none():
    """Target lines not sorted at all if target sort order is None."""
    input_lines = ["aiz\n", "aia\n"]
    expected_lines = ["aiz\n", "aia\n"]
    sortorder = None
    actual_lines = _dsusort_lines(input_lines, sortorder)
    assert expected_lines == actual_lines


def test_lines_sorted_on_whole_line_if_sortorder_is_zero():
    """Target lines sorted on entire line if sort order is zero."""
    input_lines = ["aiz zzz\n", "aia acc\n", "aia aaa\n"]
    expected_lines = ["aia aaa\n", "aia acc\n", "aiz zzz\n"]
    sortorder = 0
    actual_lines = _dsusort_lines(input_lines, sortorder)
    assert expected_lines == actual_lines


def test_target_lines_sorted_correctly_if_target_sortorder_is_greater_than_zero():
    """Target lines are sorted (on entire line) if target sort order is None."""
    input_lines = ["aiz zzz\n", "aia acc\n", "aza aaa\n"]
    expected_lines = ["aza aaa\n", "aia acc\n", "aiz zzz\n"]
    sortorder = 2
    actual_lines = _dsusort_lines(input_lines, sortorder)
    assert expected_lines == actual_lines
