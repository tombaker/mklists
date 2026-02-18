"""Generic utility functions used across the mklists codebase."""

from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any
import yaml


def deepmerge_dicts(
    base_dict: dict[str, Any],
    override_dict: dict[str, Any],
) -> dict[str, Any]:
    """Recursively merge override dict into base dict.

    Args:
        base_dict: Base dictionary.
        override_dict: Dictionary with items that override items in base dictionary.

    Note:
    - dicts are merged
    - all other values (including lists) are replaced
    """
    result = deepcopy(base_dict)

    for key, override_value in override_dict.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(override_value, dict)
        ):
            result[key] = deepmerge_dicts(result[key], override_value)
        else:
            result[key] = override_value

    return result


def load_yaml_from_file(yamlfile: Path | str) -> Any:
    """Load YAML from file.

    Args:
        yamlfile: Path to YAML file.

    Returns:
        Python object decoded from YAML.

    Raises:
        FileNotFoundError: If file does not exist.
        yaml.YAMLError: If YAML is invalid.
    """
    yamlfile = Path(yamlfile)

    if not yamlfile.exists():
        raise FileNotFoundError(f"YAML file not found: {yamlfile}")

    with yamlfile.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_yaml_from_string(yamltext: str) -> Any:
    """Load YAML string, returning dict.

    Args:
        yamltext: YAML string.

    Returns:
        Python dictionary from YAML string.

    Raises:
        yaml.YAMLError: If YAML is invalid.
    """
    # yaml.safe_load raises YAMLError if YAML is invalid.
    return yaml.safe_load(yamltext)


def make_timestamp() -> str:
    """Make timestamp."""
    return datetime.now().strftime("%Y-%m-%d_%H%M_%S%f")
