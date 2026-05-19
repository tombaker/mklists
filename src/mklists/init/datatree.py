"""Initialize a mklists datatree."""

from pathlib import Path

from mklists.config.defaults import DEFAULT_CONFIG_YAML
from mklists.errors import InitError
from mklists.init.datadir import EXAMPLE_RULES

_CONFLICT_MARKERS = [".rules", ".mklistsrc", "mklists.yaml", "mklists.rules"]


def _check_no_conflicts(path: Path) -> None:
    """Raise InitError if path already contains any mklists marker file."""
    for marker in _CONFLICT_MARKERS:
        if (path / marker).exists():
            raise InitError(f"{path / marker} already exists.")


def init_datatree(path: Path) -> list[Path]:
    """Initialize a mklists datatree at path.

    Always creates mklists.yaml with DEFAULT_CONFIG_YAML and mklists.rules
    with EXAMPLE_RULES. No datadir subdirectories are created.
    Raises InitError if any mklists marker file already exists in path.
    Returns a list of paths of files written.
    """
    _check_no_conflicts(path)
    path.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    yaml_path = path / "mklists.yaml"
    yaml_path.write_text(DEFAULT_CONFIG_YAML)
    written.append(yaml_path)
    rules_path = path / "mklists.rules"
    rules_path.write_text(EXAMPLE_RULES)
    written.append(rules_path)
    return written
