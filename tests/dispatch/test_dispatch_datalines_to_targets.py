"""@@@"""

from dataclasses import dataclass
import re
import pytest
from mklists.dispatch import dispatch_datalines_to_targets
from mklists.errors import DataNotFoundError, RulesNotFoundError
from mklists.rules import Rule


def test_apply_rules_moves_matching_lines():
    """Minimal starter test.

    Verifies:
    - matching by field
    - movement from source to target
    - unmatched lines remain
    - sorting is applied
    - newlines are preserved
    """
    rules = [
        Rule(
            source_matchfield=1,
            source_matchpattern=re.compile(r"beta"),
            source="in",
            target="out",
            target_sortkey=0,
        )
    ]

    datalines = ["alpha one\n", "beta two\n", "beta one\n"]

    result = dispatch_datalines_to_targets(rules, datalines)

    assert result["in"] == ["alpha one\n"]
    assert result["out"] == ["beta one\n", "beta two\n"]


def test_apply_rules_fails_when_no_rules():
    """If no rules found, raise RulesNotFoundError."""
    with pytest.raises(RulesNotFoundError):
        dispatch_datalines_to_targets(rules=[], datalines=["alpha\n"])


def test_apply_rules_fails_when_no_datalines():
    """If no data lines found, raise DataNotFoundError."""
    rules = [
        Rule(
            source="in",
            target="out",
            source_matchpattern=re.compile(r".*"),
            source_matchfield=0,
            target_sortkey=0,
        )
    ]

    with pytest.raises(DataNotFoundError):
        dispatch_datalines_to_targets(rules=rules, datalines=[])


def test_apply_rules_single_rule_no_matches():
    """No data lines match "delta"."""
    rules = [
        Rule(
            source="in",
            target="out",
            source_matchpattern=re.compile(r"delta"),
            source_matchfield=1,
            target_sortkey=0,
        )
    ]

    datalines = [
        "alpha one\n",
        "beta two\n",
    ]

    result = dispatch_datalines_to_targets(rules, datalines)

    assert result["in"] == datalines
    assert result["out"] == []


def test_apply_rules_single_rule_all_lines_match():
    """All rules match r".*". Also tests whole-line sorting."""
    rules = [
        Rule(
            source="in",
            target="out",
            source_matchpattern=re.compile(r".*"),
            source_matchfield=0,
            target_sortkey=0,
        )
    ]

    datalines = [
        "beta two\n",
        "alpha one\n",
    ]

    result = dispatch_datalines_to_targets(rules, datalines)

    assert result["in"] == []
    assert result["out"] == ["alpha one\n", "beta two\n"]

def test_apply_rules_two_rules_chain_lines_through_targets():
    """Target of first rule is source of second.

    Illustrates:
    - rules are applied in order
    - lines removed from a source are not re-seen
    - intermediate targets work
    - sorting occurs per rule
    """
    rules = [
        Rule(
            source="in",
            target="mid",
            source_matchpattern=re.compile(r"beta"),
            source_matchfield=1,
            target_sortkey=0,
        ),
        Rule(
            source="mid",
            target="out",
            source_matchpattern=re.compile(r"one"),
            source_matchfield=2,
            target_sortkey=0,
        ),
    ]

    datalines = [
        "alpha one\n",
        "beta one\n",
        "beta two\n",
    ]

    result = dispatch_datalines_to_targets(rules, datalines)

    assert result["in"] == ["alpha one\n"]
    assert result["mid"] == ["beta two\n"]
    assert result["out"] == ["beta one\n"]


def test_apply_rules_sorts_target_by_field():
    """Sorting by field, not whole line."""
    rules = [
        Rule(
            source="in",
            target="out",
            source_matchpattern=re.compile(r".*"),
            source_matchfield=0,
            target_sortkey=2,  # sort on second field
        )
    ]

    datalines = ["x b\n", "x a\n", "x c\n"]

    result = dispatch_datalines_to_targets(rules, datalines)

    assert result["out"] == ["x a\n", "x b\n", "x c\n"]


def test_apply_rules_initializes_all_rule_keys():
    """All keys exist in the result, even if corresponding values are empty."""
    rules = [
        Rule(
            source="in",
            target="mid",
            source_matchpattern=re.compile(r"beta"),
            source_matchfield=1,
            target_sortkey=0,
        ),
        Rule(
            source="mid",
            target="out",
            source_matchpattern=re.compile(r"gamma"),
            source_matchfield=1,
            target_sortkey=0,
        ),
    ]

    datalines = ["alpha one\n"]

    result = dispatch_datalines_to_targets(rules, datalines)

    assert set(result.keys()) == {"in", "mid", "out"}
