"""Resolve Config from defaults and optional user config file."""

from copy import deepcopy
import difflib
from pathlib import Path
import re
from re import Pattern
from typing import Any
import yaml
from mklists.errors import ConfigError, StructureError
from mklists.config.defaults import DEFAULT_CONFIG_YAML
from mklists.config.model import (
    BackupConfig,
    LinkifyConfig,
    RoutingConfig,
    SafetyConfig,
    Config,
)
from mklists.structure.markers import DATATREE_CONFIGFILE_NAME
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

    if startdir_context.is_datatree_root:
        configfile_used = startdir_context.datatree_configfile_found
    elif startdir_context.is_datadir_selfcontained:
        configfile_used = startdir_context.datadir_configfile_found
    elif startdir_context.is_datadir_in_datatree:
        # Look up datatree config file relative to discovered config root directory.
        datatree_configfile = config_rootdir / DATATREE_CONFIGFILE_NAME
        if datatree_configfile.is_file():
            configfile_used = datatree_configfile
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
        _check_for_unknown_keys(config_user, config_defaults, configfile_used)
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


def _collect_valid_keys(d: dict[str, Any], _path: str = "") -> list[str]:
    """Return all dotted-path key names reachable from d.

    Args:
        d: Dictionary to collect key paths from.
        _path: Dot-separated prefix accumulated during recursion (internal use).

    Returns:
        Flat list of dotted-path strings such as ``['verbose', 'backup.backup_depth', ...]``.
    """
    keys: list[str] = []
    for key, value in d.items():
        full_key = f"{_path}.{key}" if _path else key
        keys.append(full_key)
        if isinstance(value, dict):
            keys.extend(_collect_valid_keys(value, full_key))
    return keys


def _check_for_unknown_keys(
    user_dict: dict[str, Any],
    defaults_dict: dict[str, Any],
    configfile: Path,
    _path: str = "",
    _valid_keys: list[str] | None = None,
) -> None:
    """Raise ConfigError if user_dict contains keys absent from defaults_dict.

    Args:
        user_dict: Config dictionary loaded from user config file.
        defaults_dict: Config dictionary loaded from built-in defaults.
        configfile: Path of the user config file (used in error messages).
        _path: Dot-separated key path accumulated during recursion (internal use).
        _valid_keys: Pre-collected list of all valid dotted-path keys (internal use).

    Raises:
        ConfigError: If any key in user_dict is not present in defaults_dict.
    """
    if _valid_keys is None:
        _valid_keys = _collect_valid_keys(defaults_dict)

    for key in user_dict:
        full_key = f"{_path}.{key}" if _path else key
        if key not in defaults_dict:
            msg = f"Config file {configfile.name!r} contains unsupported key: {full_key!r}."
            suggestions = difflib.get_close_matches(
                full_key, _valid_keys, n=2, cutoff=0.6
            )
            if suggestions:
                quoted = [f"{s!r}" for s in suggestions]
                if len(quoted) == 1:
                    msg += f" Did you mean: {quoted[0]}?"
                else:
                    msg += f" Did you mean: {quoted[0]} or {quoted[1]}?"
            raise ConfigError(msg)
        if (
            isinstance(user_dict[key], dict)
            and isinstance(defaults_dict[key], dict)
            and defaults_dict[key]
        ):
            _check_for_unknown_keys(
                user_dict[key], defaults_dict[key], configfile, full_key, _valid_keys
            )


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
        config_rootdir: Root directory of mklists datatree.

    Returns:
        Instance of BackupConfig initialized from config dictionary.

    Note:
        Assumes all required keys are present.
    """
    backup_raw = config_dict["backup"]
    backup_rootdir_raw = backup_raw["backup_rootdir"]
    backup_depth = int(backup_raw["backup_depth"])

    if backup_rootdir_raw is None:
        return BackupConfig(backup_rootdir=None, backup_depth=backup_depth)

    backup_rootdir = Path(backup_rootdir_raw)

    if not backup_rootdir.is_absolute():
        if len(backup_rootdir.parts) != 1:
            raise ValueError(
                f"{str(backup_rootdir)!r} must be directory name or absolute path, "
                "not relative."
            )
        backup_rootdir = (config_rootdir / backup_rootdir).resolve()

    return BackupConfig(backup_rootdir=backup_rootdir, backup_depth=backup_depth)


def _make_routing_config(
    *,
    config_dict: dict[str, Any],
    config_rootdir: Path,
) -> RoutingConfig:
    """Initialize instance of RoutingConfig with validated routing rules.

    Args:
        config_dict: Config dictionary as derived from YAML.
        config_rootdir: Root directory of mklists datatree.

    Returns:
        Instance of RoutingConfig initialized from config dictionary.

    Note:
        Assumes all required keys are present.
    """
    routing_raw = config_dict["routing"]
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

    return RoutingConfig(routing_dict=routing_dict)


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
        config_rootdir: Root directory of mklists datatree.

    Returns:
        Instance of LinkifyConfig initialized from config dictionary.

    Note:
        Assumes all required keys are present.
    """
    linkify_raw = config_dict["linkify"]

    def _resolve_dir(raw: str | None) -> Path | None:
        if raw is None:
            return None
        return (config_rootdir / raw).resolve()

    return LinkifyConfig(
        linkify_md_dir=_resolve_dir(linkify_raw["linkify_md_dir"]),
        linkify_html_dir=_resolve_dir(linkify_raw["linkify_html_dir"]),
    )
