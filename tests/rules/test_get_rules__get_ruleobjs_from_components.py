"""Return rule object list from list of lists of rule components."""

import pytest
import re
from mklists.rules import Rule, _get_ruleobjs_from_components

# pylint: disable=unused-argument
# In tests, fixture arguments may look like they are unused.

TEST_RULES_LIST = [
    [0, ".", "x", "lines", 0],
    [1, "NOW", "lines", "alines", 1],
    [1, "LATER", "alines", "blines", 1],
    [0, "^2020", "blines", "clines", 1],
]

TEST_RULEOBJ_LIST = [
    Rule(
        source_matchfield=0,
        source_matchpattern=re.compile("."),
        source="x",
        target="lines",
        target_sortorder=0,
    ),
    Rule(
        source_matchfield=1,
        source_matchpattern=re.compile("NOW"),
        source="lines",
        target="alines",
        target_sortorder=1,
    ),
    Rule(
        source_matchfield=1,
        source_matchpattern=re.compile("LATER"),
        source="alines",
        target="blines",
        target_sortorder=1,
    ),
    Rule(
        source_matchfield=0,
        source_matchpattern=re.compile("^2020"),
        source="blines",
        target="clines",
        target_sortorder=1,
    ),
]


def test_get_ruleobjs_from_components(reinitialize_ruleclass_variables):
    """Returns list of Rule objects from Python list of five-item lists."""
    rules_list = TEST_RULES_LIST
    expected = TEST_RULEOBJ_LIST
    real = _get_ruleobjs_from_components(rules_list)
    assert real == expected


def test_exit_if_none_is_passed_as_argument(reinitialize_ruleclass_variables):
    """Raises NoRulesError if no rules list is specified as argument."""
    with pytest.raises(SystemExit):
        _get_ruleobjs_from_components(pyobj=None)


def test_exit_if_result_is_empty(reinitialize_ruleclass_variables):
    """Raises NoRulesError if no valid rules are found (ie, empty rule set)."""
    list_of_empty_lists = [[], []]
    with pytest.raises(SystemExit):
        _get_ruleobjs_from_components(list_of_empty_lists)


def test_exit_if_passed_unexpected_object(reinitialize_ruleclass_variables):
    """Raises NoRulesError if no valid rules are found (ie, empty rule set)."""
    unexpected_object = {1: 2, 2: 3}
    with pytest.raises(SystemExit):
        _get_ruleobjs_from_components(unexpected_object)


def test_exit_if_passed_empty_list(reinitialize_ruleclass_variables):
    """Raises NoRulesError if no valid rules are found (ie, empty rule set)."""
    empty_list = []
    with pytest.raises(SystemExit):
        _get_ruleobjs_from_components(empty_list)
