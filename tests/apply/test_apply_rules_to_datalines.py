"""Returns dictionary (keys are filenames, values are lists of text lines),
given list of rule objects and list of text lines aggregated from data files."""

import pytest
from mklists.rules import Rule
from mklists.apply import apply_rules_to_datalines

# pylint: disable=expression-not-assigned
# Right, because these are tests...


@pytest.mark.skip
def test_return_names2lines_dict_correct_result_too():
    """Returns correct dictionary from good inputs."""
    rules = [Rule(1, ".", "a.txt", "now.txt", 1)]
    lines = ["LATER Winter\n", "NOW Summer\n"]
    result_dict = {"now.txt": ["NOW Summer\n", "LATER Winter\n"], "a.txt": []}
    assert apply_rules_to_datalines(rules=rules, datalines=lines) == result_dict


@pytest.mark.skip
def test_target_lines_not_sorted_at_all_if_target_sortorder_is_none():
    """Target lines are not sorted at all if target sort order is None."""
    rules = [Rule(1, "i", "a.txt", "b.txt", None)]
    lines = ["aiz\n", "aia\n"]
    resulting_dict = apply_rules_to_datalines(rules, lines)
    expected_dict = {"b.txt": ["aiz\n", "aia\n"]}
    assert expected_dict == resulting_dict


@pytest.mark.skip
def test_target_lines_sorted_on_whole_line_if_target_sortorder_is_zero():
    """Target lines are sorted (on entire line) if target sort order is zero."""
    rules = [Rule(0, "i", "a.txt", "b.txt", 0)]
    lines = ["aiz zzz\n", "aia aaa\n"]
    result_dict = {"b.txt": ["aia aaa zzz\n", "aiz zzz xxx\n"]}
    assert apply_rules_to_datalines(rules=rules, datalines=lines) == result_dict


@pytest.mark.skip
def test_target_lines_sorted_correctly_if_target_sortorder_is_greater_than_zero():
    """Target lines are sorted (on entire line) if target sort order is None."""
    rules = [Rule(0, "i", "a.txt", "b.txt", 1)]
    lines = ["aia zzz\n", "aiz aaa\n"]
    result_dict = {"b.txt": ["aiz aaa\n", "aia zzz\n"]}
    assert apply_rules_to_datalines(rules=rules, datalines=lines) == result_dict


@pytest.mark.skip
def test_return_names2lines_dict_correct_result():
    """Returns correct dictionary from good inputs."""
    rules = [Rule(0, "i", "a.txt", "b.txt", 0)]
    lines = ["two ticks\n", "an ant\n", "the mite\n"]
    result_dict = {"a.txt": ["an ant\n"], "b.txt": ["two ticks\n", "the mite\n"]}
    assert apply_rules_to_datalines(rules=rules, datalines=lines) == result_dict


@pytest.mark.skip
def test_return_names2lines_dict_another_correct_result():
    """Returns correct dictionary from good inputs."""
    rules = [Rule(2, "i", "a.txt", "b.txt", 1)]
    lines = ["two ticks\n", "an ant\n", "the mite\n"]
    result_dict = {"a.txt": ["an ant\n"], "b.txt": ["the mite\n", "two ticks\n"]}
    assert apply_rules_to_datalines(rules=rules, datalines=lines) == result_dict


@pytest.mark.skip
def test_return_names2lines_dict_yet_another_correct_result():
    """Returns correct dictionary from good inputs."""
    rules = [
        Rule(1, "NOW", "a.txt", "now.txt", 0),
        Rule(1, "LATER", "a.txt", "later.txt", 0),
    ]
    lines = ["NOW Summer\n", "LATER Winter\n"]
    result_dict = {
        "now.txt": ["NOW Summer\n"],
        "later.txt": ["LATER Winter\n"],
        "a.txt": [],
    }
    assert apply_rules_to_datalines(rules=rules, datalines=lines) == result_dict


def test_return_names2lines_dict_no_rules_specified():
    """Exits with error if list of rule objects is not passed as an argument."""
    lines = [["a line\n"]]
    with pytest.raises(SystemExit):
        apply_rules_to_datalines(rules=None, datalines=lines)


def test_return_names2lines_dict_no_rules_specified_either():
    """Exits with error if list of rule objects, passed as argument, is empty."""
    rules = []
    lines = ["NOW Summer\n", "LATER Winter\n"]
    with pytest.raises(SystemExit):
        apply_rules_to_datalines(rules=rules, datalines=lines)


def test_return_names2lines_dict_no_data_specified():
    """Exits with error no datalines list is passed as argument."""
    rules = [[Rule(1, "a", "b", "c", 2)]]
    with pytest.raises(SystemExit):
        apply_rules_to_datalines(rules=rules, datalines=None)


def test_return_names2lines_dict_no_data_specified_either():
    """Exits with error if datalines list passed as argument is empty."""
    rules = [
        Rule(1, "NOW", "a.txt", "now.txt", 0),
        Rule(1, "LATER", "a.txt", "later.txt", 0),
    ]
    lines = []
    with pytest.raises(SystemExit):
        apply_rules_to_datalines(rules=rules, datalines=lines)
