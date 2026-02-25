"""Tests $MKLMKL/rules.py"""

import re
from pathlib import Path
import pytest
from mklists.errors import RuleError
from mklists.rules.model import Rule
from mklists.rules.load import load_rules_for_datadir


def write_rulefile(path: Path, lines: list[str]) -> None:
    """Helper."""
    path.write_text("\n".join(lines) + "\n")


def test_single_rulefile(tmp_path):
    """Shows concatenation."""
    rulefile = tmp_path / ".rules"

    write_rulefile(
        rulefile,
        [
            "0|foo|A|B|",
        ],
    )

    rules = load_rules_for_datadir([rulefile])

    assert rules == [
        Rule(
            source_matchfield=0,
            source_matchpattern=re.compile("foo"),
            source="A",
            target="B",
            target_sortkey=None,
        )
    ]


def test_multiple_rulefiles_merge_in_order(tmp_path):
    """Rulefiles are processed and merged in order."""
    repo = tmp_path / "mklists.rules"
    local = tmp_path / ".rules"

    write_rulefile(repo, ["0|foo|A|B|"])
    write_rulefile(local, ["0|bar|B|C|"])

    rules = load_rules_for_datadir([repo, local])

    assert rules == [
        Rule(
            source_matchfield=0,
            source_matchpattern=re.compile("foo"),
            source="A",
            target="B",
            target_sortkey=None,
        ),
        Rule(
            source_matchfield=0,
            source_matchpattern=re.compile("bar"),
            source="B",
            target="C",
            target_sortkey=None,
        ),
    ]


def test_rule_order_matters(tmp_path):
    """Rules are out of order, fail chain validation, RuleError is raised."""
    repo = tmp_path / "mklists.rules"
    local = tmp_path / ".rules"

    write_rulefile(repo, ["0|foo|A|B|"])
    write_rulefile(local, ["0|bar|B|C|"])

    with pytest.raises(RuleError):
        load_rules_for_datadir([local, repo])


def test_empty_rulefile_ok(tmp_path):
    """Empty rulefile is okay."""
    repo = tmp_path / "mklists.rules"
    local = tmp_path / ".rules"

    write_rulefile(repo, [])
    write_rulefile(local, ["0|bar|A|B|"])

    rules = load_rules_for_datadir([repo, local])

    assert rules == [
        Rule(
            source_matchfield=0,
            source_matchpattern=re.compile("bar"),
            source="A",
            target="B",
            target_sortkey=None,
        )
    ]


def test_missing_rulefile_raises(tmp_path):
    """If rulefile is not found, FileNotFoundError; should not happen in practice."""
    missing = tmp_path / "does_not_exist.rules"

    with pytest.raises(FileNotFoundError):
        load_rules_for_datadir([missing])
