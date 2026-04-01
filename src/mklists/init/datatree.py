"""Initialize a mklists datatree."""

from pathlib import Path

from mklists.errors import InitError
from mklists.init.datadir import EXAMPLE_RULES

_CONFLICT_MARKERS = [".rules", ".mklistsrc", "mklists.yaml", "mklists.rules"]


def _check_no_conflicts(path: Path, subdirs: tuple[str, ...]) -> None:
    """Raise InitError if path contains any mklists marker file or named subdir."""
    for marker in _CONFLICT_MARKERS:
        if (path / marker).exists():
            raise InitError(f"{path / marker} already exists.")
    for subdir in subdirs:
        if (path / subdir).exists():
            raise InitError(f"{path / subdir} already exists.")


def init_datatree(
    path: Path,
    rules: bool = False,
    subdirs: tuple[str, ...] = ("a", "b"),
) -> None:
    """Initialize a mklists datatree at path.

    Always creates mklists.yaml, mklists.rules, and subdirectories each
    containing an empty .rules file.
    If rules is True, populates all rule files with commented example content.
    Raises InitError if any mklists marker file or named subdir already exists.
    """
    _check_no_conflicts(path, subdirs)
    path.mkdir(parents=True, exist_ok=True)
    rules_content = EXAMPLE_RULES if rules else ""
    (path / "mklists.yaml").write_text("")
    (path / "mklists.rules").write_text(rules_content)
    for subdir in subdirs:
        subdir_path = path / subdir
        subdir_path.mkdir()
        (subdir_path / ".rules").write_text(rules_content)
