"""Tests ~/github/tombaker/mklists/src/mklists/rules.py"""

from pathlib import Path
import pytest
from mklists.rules import _iter_rulelines


def write(tmp_ruledir: Path, text: str) -> Path:
    """Helper to write temporary rule file.

    Args:
        tmp_ruledir: Temporary path used for a specific Pytest test run.
        text: Rule file text to be written to a temporary rule file.

    Returns:
        Rule file, as Path object, written to temporary test run directory.
    """
    path = tmp_ruledir / "rules.conf"
    path.write_text(text)

    return path


def test_ignores_blank_lines(tmp_path):
    """Blank lines in rule file are ignored."""
    path = write(tmp_path, "\n\n\n")

    assert list(_iter_rulelines(path)) == []


def test_ignores_comment_lines(tmp_path):
    """Comment lines are ignored."""
    path = write(tmp_path, "# comment\n# another comment\n   # indented comment\n")

    assert list(_iter_rulelines(path)) == []


def test_strips_leading_whitespace(tmp_path):
    """Leading whitespace is stripped."""
    path = write(
        tmp_path,
        """
            0|.|lines|__RENAME__|
                1|DOMAINS|__RENAME__|domains|
        """,
    )

    assert list(_iter_rulelines(path)) == [
        "0|.|lines|__RENAME__|",
        "1|DOMAINS|__RENAME__|domains|",
    ]


def test_mixed_content(tmp_path):
    """Another example with mixture of blank lines, whitespace, and comments."""
    path = write(
        tmp_path,
        """
        # header comment

            0|.|lines|__RENAME__|

        # section
            1|DOMAINS|__RENAME__|domains|
                2|GANDI|domains|domains_gandi|

        """,
    )

    assert list(_iter_rulelines(path)) == [
        "0|.|lines|__RENAME__|",
        "1|DOMAINS|__RENAME__|domains|",
        "2|GANDI|domains|domains_gandi|",
    ]


def test_preserves_internal_whitespace(tmp_path):
    """Whitespace within a rule line is preserved."""
    path = write(tmp_path, "0|foo bar|baz qux|__RENAME__|\n")

    assert list(_iter_rulelines(path)) == [
        "0|foo bar|baz qux|__RENAME__|",
    ]
