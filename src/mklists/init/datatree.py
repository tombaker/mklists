"""Initialize a mklists datatree."""

from pathlib import Path

from mklists.config.defaults import DEFAULT_CONFIG_YAML
from mklists.init.datadir import EXAMPLE_RULES, check_no_conflicts


def init_datatree(path: Path) -> list[Path]:
    """Initialize a mklists datatree at path.

    Always creates mklists.yaml with DEFAULT_CONFIG_YAML and mklists.rules
    with EXAMPLE_RULES. No datadir subdirectories are created.
    Raises InitError if any mklists marker file already exists in path.
    Returns a list of paths of files written.
    """
    check_no_conflicts(path)
    path.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    yaml_path = path / "mklists.yaml"
    yaml_path.write_text(DEFAULT_CONFIG_YAML)
    written.append(yaml_path)
    rules_path = path / "mklists.rules"
    rules_path.write_text(EXAMPLE_RULES)
    written.append(rules_path)
    return written
