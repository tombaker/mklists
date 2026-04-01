"""Initialize a mklists datadir."""

from pathlib import Path

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


def _check_no_conflicts(path: Path) -> None:
    """Raise InitError if path already contains any mklists marker file."""
    for marker in _CONFLICT_MARKERS:
        if (path / marker).exists():
            raise InitError(f"{path / marker} already exists.")


def init_datadir(
    path: Path,
    rules: bool = False,
    self_contained: bool = False,
) -> None:
    """Initialize a mklists datadir at path.

    Always creates an empty .rules file as a structural marker.
    If rules is True, populates .rules with commented example content.
    If self_contained is True, also creates an empty .mklistsrc.
    Raises InitError if any mklists marker file already exists in path.
    """
    _check_no_conflicts(path)
    path.mkdir(parents=True, exist_ok=True)
    rules_content = EXAMPLE_RULES if rules else ""
    (path / ".rules").write_text(rules_content)
    if self_contained:
        (path / ".mklistsrc").write_text("")
