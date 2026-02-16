"""Tests ~/github/tombaker/mklists/src/mklists/rules.py"""

import pytest
from mklists.rules import Rule, RuleError, _validate_rulechain


def minimal_rule(source, target):
    """Helper that creates minimal Rule object for chain testing."""
    return Rule(
        source_matchfield=1,  # not relevant here
        source_matchpattern=None,  # not relevant here
        source=source,
        target=target,
        target_sortkey=1,  # not relevant here
    )


def test_empty_rule_chain_is_valid():
    """Empty rule chain is valid."""
    _validate_rulechain([])


def test_single_rule_chain_is_valid():
    """Rule chain with single rule is valid."""
    rules = [
        minimal_rule("A", "B"),
    ]
    _validate_rulechain(rules)


def test_valid_rule_chain_with_progressive_sources():
    """Sources can come from previous targets."""
    rules = [
        minimal_rule("A", "B"),
        minimal_rule("B", "C"),  # B was a target
        minimal_rule("C", "D"),
    ]
    _validate_rulechain(rules)


def test_later_rule_with_unseen_source_raises_error():
    """Rule with unseen source raises error."""
    rules = [
        minimal_rule("A", "B"),
        minimal_rule("B", "C"),
        minimal_rule("X", "D"),  # X never seen
    ]

    with pytest.raises(RuleError):
        _validate_rulechain(rules)
