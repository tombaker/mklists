"""Initialize a mklists datatree."""

from pathlib import Path

from mklists.config.defaults import DEFAULT_CONFIG_YAML
from mklists.errors import InitError
from mklists.init.datadir import EXAMPLE_RULES

_CONFLICT_MARKERS = [".rules", ".mklistsrc", "mklists.yaml", "mklists.rules"]


def _check_no_conflicts(path: Path, datadirs: tuple[str, ...]) -> None:
    """Raise InitError if path contains any mklists marker file or named datadir."""
    for marker in _CONFLICT_MARKERS:
        if (path / marker).exists():
            raise InitError(f"{path / marker} already exists.")
    for datadir in datadirs:
        if (path / datadir).exists():
            raise InitError(f"{path / datadir} already exists.")


def init_datatree(
    path: Path,
    rules: bool = False,
    datadirs: tuple[str, ...] = ("a", "b"),
) -> list[Path]:
    """Initialize a mklists datatree at path.

    Always creates mklists.yaml and mklists.rules.
    Creates a subdirectory with an empty .rules file for each name in datadirs.
    If rules is True, populates all rule files with commented example content.
    Raises InitError if any mklists marker file or named datadir already exists.
    Returns a list of paths of files written.
    """
    _check_no_conflicts(path, datadirs)
    path.mkdir(parents=True, exist_ok=True)
    rules_content = EXAMPLE_RULES if rules else ""
    written: list[Path] = []
    yaml_path = path / "mklists.yaml"
    yaml_path.write_text(DEFAULT_CONFIG_YAML)
    written.append(yaml_path)
    rules_path = path / "mklists.rules"
    rules_path.write_text(rules_content)
    written.append(rules_path)
    for datadir in datadirs:
        datadir_path = path / datadir
        datadir_path.mkdir()
        datadir_rules_path = datadir_path / ".rules"
        datadir_rules_path.write_text(rules_content)
        written.append(datadir_rules_path)
    return written
