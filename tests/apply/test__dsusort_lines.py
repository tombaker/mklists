"""@@@Docstring"""

from mklists.apply import _dsusort_lines


def test_lines_not_sorted_if_sortorder_is_none():
    """Lines left unsorted if sort order is None."""
    input_lines = ["aiz\n", "aia\n"]
    expected_output = ["aiz\n", "aia\n"]
    sortorder = None
    actual_output = _dsusort_lines(input_lines, sortorder)
    assert expected_output == actual_output


def test_lines_not_sorted_if_sortorder_greater_than_fields_in_line():
    """Lines left unsorted if sort order greater than number of fields in line."""
    input_lines = ["aiz\n", "aia\n"]
    expected_output = ["aiz\n", "aia\n"]
    sortorder = 7
    actual_output = _dsusort_lines(input_lines, sortorder)
    assert expected_output == actual_output


def test_lines_sorted_on_whole_line_if_sortorder_is_zero():
    """Target lines sorted on entire line if sort order is zero."""
    input_lines = ["aiz zzz\n", "aia acc\n", "aia aaa\n"]
    expected_output = ["aia aaa\n", "aia acc\n", "aiz zzz\n"]
    sortorder = 0
    actual_output = _dsusort_lines(input_lines, sortorder)
    assert expected_output == actual_output


def test_sort_on_field4_where_not_all_lines_have_four_fields():
    """Lines with less fields than sortorder get sorted first."""
    input_lines = ["f g h i j\n", "a b c d e\n", "k l m\n"]
    expected_output = ["k l m\n", "a b c d e\n", "f g h i j\n"]
    sortorder = 4
    actual_output = _dsusort_lines(input_lines, sortorder)
    assert actual_output == expected_output


# ['the tick\n', 'two mites\n']
# @pytest.mark.skip
# def test_sort_on_field3():
#     input_lines = ["a b c d e\n", "f g h i j\n", "k l m\n"]
#     # [("c", "a b c d e\n"), ("h", "f g h i j\n"), ("m", "k l m\n")]
#     expected_output = ["a b c d e\n", "f g h i j\n", "k l m\n"]
#     sortorder = 3
#     actual_output = _dsusort_lines(input_lines, sortorder)
#     assert actual_output == expected_output
#
#
