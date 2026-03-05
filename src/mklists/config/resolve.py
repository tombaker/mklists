"""Resolve Config from defaults and optional user config file."""

from copy import deepcopy
from pathlib import Path
import re
from re import Pattern
from typing import Any
import yaml
from mklists.errors import StructureError
from mklists.config.defaults import DEFAULT_CONFIG_YAML
from mklists.config.model import (
    BackupConfig,
    LinkifyConfig,
    RoutingConfig,
    SafetyConfig,
    Config,
)
from mklists.structure.markers import REPO_CONFIGFILE_NAME
from mklists.structure.model import StructuralContext


def resolve_config(structural_context: StructuralContext) -> Config:
    """Derive settings from built-in defaults and optional user-defined config file.

    Args:
        structural_context: Resolved execution context for one Mklists run.

    Returns:
        Instance of Config.
    """
    startdir_context = structural_context.startdir_context
    config_rootdir = startdir_context.config_rootdir

    if startdir_context.is_repo_root:
        configfile_used = startdir_context.repo_configfile_found
    elif startdir_context.is_datadir_selfcontained:
        configfile_used = startdir_context.datadir_configfile_found
    elif startdir_context.is_datadir_in_repo:
        # Look up repo config file relative to discovered config root directory.
        repo_configfile = config_rootdir / REPO_CONFIGFILE_NAME
        if repo_configfile.is_file():
            configfile_used = repo_configfile
        else:
            configfile_used = None
    else:
        raise StructureError("Unreachable structural state.")

    config_dict = _load_merged_configdict(configfile_used=configfile_used)

    return Config(
        configfile_used=configfile_used,
        config_rootdir=config_rootdir,
        verbose=config_dict["verbose"],
        backup=_make_backup_config(
            config_dict=config_dict, config_rootdir=config_rootdir
        ),
        linkify=_make_linkify_config(
            config_dict=config_dict, config_rootdir=config_rootdir
        ),
        routing=_make_routing_config(
            config_dict=config_dict, config_rootdir=config_rootdir
        ),
        safety=_make_safety_config(config_dict=config_dict),
    )


def _deepmerge_dicts(
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
            result[key] = _deepmerge_dicts(result[key], override_value)
        else:
            result[key] = override_value

    return result


def _load_merged_configdict(configfile_used: Path | None) -> dict[str, Any]:
    """Load default YAML config and merge optional user YAML config.

    Args:
        configfile_used: Path of user config file (or None if none exists).

    Returns:
        Merged configuration dictionary.
    """
    config_defaults = _load_yaml_from_string(DEFAULT_CONFIG_YAML) or {}
    if not isinstance(config_defaults, dict):
        raise TypeError("DEFAULT_CONFIG_YAML must decode to a mapping.")

    if configfile_used is not None:
        config_user = _load_yaml_from_file(configfile_used) or {}
        if not isinstance(config_user, dict):
            raise TypeError("User config YAML must decode to a mapping.")
    else:
        config_user = {}

    return _merge_config_dicts(config_defaults, config_user)


def _load_yaml_from_file(yamlfile: Path | str) -> Any:
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
        raise FileNotFoundError(f"YAML file not found: {yamlfile!r}.")

    with yamlfile.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_yaml_from_string(yamltext: str) -> Any:
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


def _merge_config_dicts(
    defaults: dict[str, Any],
    overrides: dict[str, Any],
) -> dict[str, Any]:
    """Merge overrides config over defaults.

    Args:
        defaults: Dictionary of built-in default config settings.
        overrides: Dictionary of user-defined override settings.

    Returns:
        Merged dictionary of built-in defaults and override settings.
    """
    if not overrides:
        return deepcopy(defaults)

    return _deepmerge_dicts(defaults, overrides)


def _make_backup_config(
    *,
    config_dict: dict[str, Any],
    config_rootdir: Path,
) -> BackupConfig:
    """Initialize instance of BackupConfig.

    Args:
        config_dict: Config dictionary as derived from YAML.
        config_rootdir: Root directory of mklists repo.

    Returns:
        Instance of BackupConfig initialized from config dictionary.

    Note:
        Assumes all required keys are present.
    """
    backup_raw = config_dict["backup"]
    backup_rootdir_raw = backup_raw["backup_rootdir"]

    if backup_rootdir_raw is None:
        raise ValueError("backup_rootdir must not be configured as null.")

    backup_rootdir = Path(backup_rootdir_raw)

    if not backup_rootdir.is_absolute():
        if len(backup_rootdir.parts) != 1:
            raise ValueError(
                f"{str(backup_rootdir)!r} must be directory name or absolute path, "
                "not relative."
            )
        backup_rootdir = (config_rootdir / backup_rootdir).resolve()

    return BackupConfig(
        backup_enabled=bool(backup_raw["backup_enabled"]),
        backup_rootdir=backup_rootdir,
        backup_depth=int(backup_raw["backup_depth"]),
    )


def _make_routing_config(
    *,
    config_dict: dict[str, Any],
    config_rootdir: Path,
) -> RoutingConfig:
    """Initialize instance of RoutingConfig with validated routing rules.

    Args:
        config_dict: Config dictionary as derived from YAML.
        config_rootdir: Root directory of mklists repo.

    Returns:
        Instance of RoutingConfig initialized from config dictionary.

    Note:
        Assumes all required keys are present.
    """
    routing_raw = config_dict["routing"]
    routing_enabled = bool(routing_raw["routing_enabled"])
    files2dirs_raw = routing_raw["routing_dict"]

    routing_dict: dict[str, Path] = {}

    for filename, dirname in files2dirs_raw.items():
        # --- Validate filename (key) ---
        if len(Path(filename).parts) != 1:
            raise ValueError(
                f"filename {filename!r} must be a single filename, not a path."
            )

        # --- Validate / normalize dirname (value) ---
        if not Path(dirname).is_absolute() and len(Path(dirname).parts) != 1:
            raise ValueError(
                f"{dirname!r} (in `routing_dict`) must be a directory name or "
                "absolute path, not a relative path."
            )

        routing_dict[filename] = (config_rootdir / dirname).resolve()

    return RoutingConfig(
        routing_enabled=routing_enabled,
        routing_dict=routing_dict,
    )


def _make_safety_config(config_dict: dict[str, Any]) -> SafetyConfig:
    """Initialize instance of SafetyConfig.

    Args:
        config_dict: Config dictionary as derived from YAML.

    Returns:
        Instance of SafetyConfig initialized from config dictionary.

    Note:
        Assumes all required keys are present.
    """
    safety_raw = config_dict["safety"]

    invalid_patterns: list[Pattern[str]] = []
    for pat in safety_raw["invalid_filename_patterns"]:
        try:
            invalid_patterns.append(re.compile(pat))
        except re.error as e:
            raise ValueError(f"Invalid regex in config: {pat!r}") from e

    return SafetyConfig(invalid_filename_patterns=invalid_patterns)


def _make_linkify_config(
    *,
    config_dict: dict[str, Any],
    config_rootdir: Path,
) -> LinkifyConfig:
    """Initialize instance of LinkifyConfig.

    Args:
        config_dict: Config dictionary as derived from YAML.
        config_rootdir: Root directory of mklists repo.

    Returns:
        Instance of LinkifyConfig initialized from config dictionary.

    Note:
        Assumes all required keys are present.
    """
    linkify_raw = config_dict["linkify"]
    linkify_dir_raw = linkify_raw["linkify_dir"]

    if linkify_dir_raw is None:
        raise ValueError("linkify_dir must not be configured as null.")

    return LinkifyConfig(
        linkify_enabled=bool(linkify_raw["linkify_enabled"]),
        linkify_dir=(config_rootdir / linkify_dir_raw).resolve(),
    )
