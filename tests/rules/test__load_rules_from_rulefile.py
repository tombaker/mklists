"""Tests $MKLMKL/rules.py"""

from pathlib import Path
import re
import pytest
from mklists.errors import RuleError
from mklists.rules import _load_rules_from_rulefile, Rule


def write_rulefile(tmp_ruledir: Path, text_to_write: str) -> Path:
    """Test helper that writes given text to tmp_ruledir/rules.txt.

    Args:
        tmp_ruledir: Path for directory where rules.txt to be written.
        text_to_write: Text to be written to rules.txt.

    Returns:
        Path for written rule file.
    """
    rulefile = tmp_ruledir / "rules.txt"
    rulefile.write_text(text_to_write)
    return rulefile


def test_empty_rulefile_returns_empty_list(tmp_path):
    """If rulefile is empty, list returned is also empty."""
    rulefile = write_rulefile(tmp_ruledir=tmp_path, text_to_write="")
    rules = _load_rules_from_rulefile(rulefile)
    # pylint: disable=use-implicit-booleaness-not-comparison
    assert rules == []


def test_comments_and_blank_lines_are_ignored(tmp_path):
    """Comments and blank lines are ignored."""
    rulefile = write_rulefile(
        tmp_ruledir=tmp_path,
        text_to_write="""
        # this is a comment

        # another comment

        """,
    )

    rules = _load_rules_from_rulefile(rulefile)

    # pylint: disable=use-implicit-booleaness-not-comparison
    assert rules == []


def test_single_valid_rule_is_loaded(tmp_path):
    """Single rule loaded is valid."""
    rulefile = write_rulefile(
        tmp_ruledir=tmp_path,
        text_to_write="""
        1|^abc$|source|target|1
        """,
    )

    actual_rules_list = _load_rules_from_rulefile(rulefile)

    expected_rules_list = [
        Rule(
            source_matchfield=1,
            source_matchpattern=re.compile("^abc$"),
            source="source",
            target="target",
            target_sortkey=1,
        )
    ]

    assert expected_rules_list == actual_rules_list


def test_valid_rule_chain_is_loaded(tmp_path):
    """Rule chain loaded is valid."""
    rulefile = write_rulefile(
        tmp_ruledir=tmp_path,
        text_to_write="""
        1|.*|A|B|1
        1|.*|B|C|1
        1|.*|C|D|1
        """,
    )

    rules = _load_rules_from_rulefile(rulefile)

    assert [r.source for r in rules] == ["A", "B", "C"]
    assert [r.target for r in rules] == ["B", "C", "D"]


def test_invalid_rule_format_raises_error(tmp_path):
    """If rule lacks a required field, raise RuleError."""
    rulefile = write_rulefile(
        tmp_ruledir=tmp_path,
        text_to_write="""
        1|.*|A|B
        """,
    )

    with pytest.raises(RuleError):
        _load_rules_from_rulefile(rulefile)
