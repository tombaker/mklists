"""Returns dictionary (keys are filenames, values are lists of text lines),
given list of rule objects and list of text lines aggregated from data files."""

import pytest
from mklists.rules import Rule
from mklists.apply import apply_rules_to_datalines

# pylint: disable=expression-not-assigned
# Right, because these are tests...


@pytest.mark.skip
def test_return_names2lines_dict_another_correct_result():
    """Returns correct dictionary from good inputs."""
    rules = [Rule(2, "i", "a.txt", "b.txt", 1)]
    lines = ["the tick\n", "an ant\n", "two mites\n"]
    result_dict = {"a.txt": ["an ant\n"], "b.txt": ["two mites\n", "the tick\n"]}
    actual_dict = apply_rules_to_datalines(rules=rules, datalines=lines)
    assert actual_dict == result_dict


@pytest.mark.skip
def test_return_n2l_dict_given_good_inputs():
    """Returns correct dictionary from good inputs."""
    rules = [Rule(0, "i", "a.txt", "b.txt", 0)]
    lines = ["two ticks\n", "an ant\n", "the mite\n"]
    result_dict = {"a.txt": ["an ant\n"], "b.txt": ["two ticks\n", "the mite\n"]}
    actual_dict = apply_rules_to_datalines(rules=rules, datalines=lines)
    assert actual_dict == result_dict


def test_all_lines_moved_to_target():
    """Returns correct dictionary where all lines moved to target."""
    rules = [Rule(1, ".", "a.txt", "b.txt", None)]
    lines = ["LATER Winter\n", "NOW Summer\n"]
    expected_dict = {"a.txt": [], "b.txt": ["LATER Winter\n", "NOW Summer\n"]}
    actual_dict = apply_rules_to_datalines(rules=rules, datalines=lines)
    assert actual_dict == expected_dict


def test_two_rules_and_original_source_now_empty():
    """After processing two rules, lines now in values of new source keys."""
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
    actual_dict = apply_rules_to_datalines(rules, lines)
    assert actual_dict == result_dict


def test_exits_when_no_rulelist_specified():
    """Exits with error if list of rule objects is not passed as an argument."""
    lines = [["a line\n"]]
    with pytest.raises(SystemExit):
        apply_rules_to_datalines(rules=None, datalines=lines)


def test_exits_when_passed_empty_rule_list():
    """Exits with error if list of rule objects, passed as argument, is empty."""
    rules = []
    lines = ["NOW Summer\n", "LATER Winter\n"]
    with pytest.raises(SystemExit):
        apply_rules_to_datalines(rules=rules, datalines=lines)


def test_exits_when_no_data_specified():
    """Exits with error no datalines list is passed as argument."""
    rules = [[Rule(1, "a", "b", "c", 2)]]
    with pytest.raises(SystemExit):
        apply_rules_to_datalines(rules=rules, datalines=None)


def test_exits_when_passed_empty_datalines_list():
    """Exits with error if datalines list passed as argument is empty."""
    rules = [
        Rule(1, "NOW", "a.txt", "now.txt", 0),
        Rule(1, "LATER", "a.txt", "later.txt", 0),
    ]
    lines = []
    with pytest.raises(SystemExit):
        apply_rules_to_datalines(rules=rules, datalines=lines)
