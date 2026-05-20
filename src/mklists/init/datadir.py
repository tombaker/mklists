"""Initialize a mklists datadir."""

from pathlib import Path

from mklists.config.defaults import DEFAULT_CONFIG_YAML
from mklists.errors import InitError

EXAMPLE_RULES = """\
# Rule format: matchfield|pattern|source|target|sortkey
#   matchfield: 0 = whole line, 1+ = whitespace-delimited field
#   pattern:    regular expression
#   source:     file lines are read from
#   target:     file lines are moved to
#   sortkey:    field to sort target by (blank = no sort)
#
# Example: move any line containing "TODO" from notes.txt to todo.txt
# 0|TODO|notes.txt|todo.txt|
#
# Example: identity rule — keep all lines in place
# 0|.|input.txt|output.txt|
"""

_CONFLICT_MARKERS = [".rules", ".mklistsrc", "mklists.yaml", "mklists.rules"]


def check_no_conflicts(path: Path) -> None:
    """Raise InitError if path already contains any mklists marker file."""
    for marker in _CONFLICT_MARKERS:
        if (path / marker).exists():
            raise InitError(f"{path / marker} already exists.")


def init_datadir(
    path: Path,
    bare: bool = False,
    self_contained: bool = False,
) -> list[Path]:
    """Initialize a mklists datadir at path.

    Always creates .rules with EXAMPLE_RULES content; empty if bare is True.
    If self_contained is True, also creates .mklistsrc with DEFAULT_CONFIG_YAML;
    empty if bare is True.
    Raises InitError if any mklists marker file already exists in path.
    Returns a list of paths of files written.
    """
    check_no_conflicts(path)
    path.mkdir(parents=True, exist_ok=True)
    rules_content = "" if bare else EXAMPLE_RULES
    written: list[Path] = []
    rules_path = path / ".rules"
    rules_path.write_text(rules_content)
    written.append(rules_path)
    if self_contained:
        mklistsrc_path = path / ".mklistsrc"
        mklistsrc_content = "" if bare else DEFAULT_CONFIG_YAML
        mklistsrc_path.write_text(mklistsrc_content)
        written.append(mklistsrc_path)
    return written
