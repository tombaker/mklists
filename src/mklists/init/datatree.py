"""Initialize a mklists datatree."""

from pathlib import Path

from mklists.config.defaults import DEFAULT_CONFIG_YAML
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
) -> list[Path]:
    """Initialize a mklists datatree at path.

    Always creates mklists.yaml, mklists.rules, and subdirectories each
    containing an empty .rules file.
    If rules is True, populates all rule files with commented example content.
    Raises InitError if any mklists marker file or named subdir already exists.
    Returns a list of paths of files written.
    """
    _check_no_conflicts(path, subdirs)
    path.mkdir(parents=True, exist_ok=True)
    rules_content = EXAMPLE_RULES if rules else ""
    written: list[Path] = []
    yaml_path = path / "mklists.yaml"
    yaml_path.write_text(DEFAULT_CONFIG_YAML)
    written.append(yaml_path)
    rules_path = path / "mklists.rules"
    rules_path.write_text(rules_content)
    written.append(rules_path)
    for subdir in subdirs:
        subdir_path = path / subdir
        subdir_path.mkdir()
        subdir_rules_path = subdir_path / ".rules"
        subdir_rules_path.write_text(rules_content)
        written.append(subdir_rules_path)
    return written
