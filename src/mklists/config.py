"""Load configuration settings from defaults and user config files."""

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Pattern
import yaml
from .rules import Rule
from .utils import deepmerge_dicts, load_yaml_from_file, load_yaml_from_string


# The complete default config schema in YAML; all required keys must appear here.
DEFAULT_CONFIG_YAML = """\
verbose: False

# Backup: Snapshot data directory for each pass to a time-stamped backup directory.
backup:
  backup_enabled: False
  backup_dir: backups
  backup_depth: 3

# Routing: Newly generated files with special names can be moved to given directories.
routing:
  routing_enabled: False
  routing_dict: {}
  ## Example:
  # routing_dict:
  #   to_a.txt: a
  #   to_b.txt: b
  #   to_bar.txt: /Users/foo/bar

# Safety: Processing halts if safety criteria are violated.
safety:
  invalid_filename_patterns:
   - \\.swp$
   - \\.tmp$
   - \\.vim$
   - "~$"

# Urlification: After processing, data files can be written in HTML to given directory.
urlify:
  urlify_enabled: False
  urlify_dir: html
"""

_CONFIG_DEFAULTS = load_yaml_from_string(DEFAULT_CONFIG_YAML)


@dataclass(slots=True, frozen=True)
class BackupConfig:
    """Policy for backing up data files before processing."""

    backup_enabled: bool
    backup_dir: Path
    backup_depth: int


@dataclass(slots=True, frozen=True)
class RoutingConfig:
    """Map of special files to specific destination directories."""

    routing_enabled: bool
    routing_dict: dict[str, Path]


@dataclass(slots=True, frozen=True)
class SafetyConfig:
    """Heuristics for rejecting unsafe filenames for data."""

    invalid_filename_patterns: list[Pattern[str]]


@dataclass(slots=True, frozen=True)
class UrlifyConfig:
    """Policy for writing data files in HTML."""

    urlify_enabled: bool
    urlify_dir: Path


@dataclass(slots=True)
class MklistsConfig:
    """Normalized, validated configuration used for processing one or more datadirs.

    A single config instance is derived from built-in defaults plus an optional
    config file. Multiple datadirs may share the same config instance when they
    share the same effective config file.
    """

    verbose: bool
    backup: BackupConfig
    routing: RoutingConfig
    safety: SafetyConfig
    urlify: UrlifyConfig


def load_config(configfile_used: Path | None) -> MklistsConfig:
    """Derive settings from built-in defaults and optional user-defined config file.

    Args:
        configfile_used: Path of user-defined config file to use, if available.

    Returns:
        Instance of configuration object MklistsConfig.

    Note:
        Is no user-defined config file is found, uses only built-in defaults.
    """
    config_dict = _load_configdict_from_yaml(configfile_used=configfile_used)
    mklists_cfg = _make_mklists_config(
        config_dict=config_dict,
        config_rootdir=config_rootdir,
    )

    return mklists_cfg


def _load_configdict_from_yaml(configfile_used: Path | None) -> dict[str, Any]:
    """Load config dictionary from YAML.

    Args:
        configfile_used: Path of user config file (or None if none exists).

    Returns:
        Merged configuration dictionary.
    """
    if configfile_used is not None:
        try:
            config_user = load_yaml_from_file(configfile_used)
        except yaml.YAMLError as e:
            raise yaml.YAMLError("Invalid user-defined YAML.") from e

        if config_user is None:
            config_user = {}
    else:
        config_user = {}

    if not isinstance(config_user, dict):
        raise TypeError("User config YAML must decode to a mapping.")

    return _merge_config_dicts(_CONFIG_DEFAULTS, config_user)


def _merge_config_dicts(
    defaults: dict[str, list[Rule]],
    overrides: dict[str, list[Rule]],
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

    return deepmerge_dicts(defaults, overrides)


def _make_backup_config(
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
    backup_dir = Path(backup_raw["backup_dir"])

    if not backup_dir.is_absolute():
        if len(backup_dir.parts) != 1:
            raise ValueError(
                "backup_dir must be single directory name or absolute pathname."
            )
        backup_dir = (config_rootdir / backup_dir).resolve()

    return BackupConfig(
        backup_enabled=bool(backup_raw["backup_enabled"]),
        backup_dir=backup_dir,
        backup_depth=int(backup_raw["backup_depth"]),
    )


def _make_routing_config(
    config_dict: dict[str, Any], config_rootdir: Path
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
        filename = Path(filename)

        if filename.is_absolute() or len(filename.parts) != 1:
            raise ValueError(
                f"routing_dict must be single filename, not a path: {filename!r} ."
            )

        # --- Validate / normalize dirname (value) ---
        dirname = Path(dirname)

        if not dirname.is_absolute():
            if len(dirname.parts) != 1:
                raise ValueError(
                    "routing_dict values must be single directory name "
                    "or an absolute pathname."
                )
            dirname = (config_rootdir / dirname).resolve()

        routing_dict[filename] = dirname

    return RoutingConfig(
        routing_enabled=routing_enabled,
        routing_dict=routing_dict,
    )


def _make_safety_config(config_dict: dict[str, Any]) -> SafetyConfig:
    """Initialize instance of SafetyConfig.

    Args:
        config_dict: Config dictionary as derived from YAML.
        config_rootdir: Root directory of mklists repo.

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


def _make_urlify_config(
    config_dict: dict[str, Any],
    config_rootdir: Path,
) -> UrlifyConfig:
    """Initialize instance of UrlifyConfig.

    Args:
        config_dict: Config dictionary as derived from YAML.
        config_rootdir: Root directory of mklists repo.

    Returns:
        Instance of UrlifyConfig initialized from config dictionary.

    Note:
        Assumes all required keys are present.
    """
    urlify_raw = config_dict["urlify"]

    return UrlifyConfig(
        urlify_enabled=bool(urlify_raw["urlify_enabled"]),
        urlify_dir=(config_rootdir / urlify_raw["urlify_dir"]).resolve(),
    )


def _make_mklists_config(
    config_dict: dict[str, Any],
    config_rootdir: Path,
) -> MklistsConfig:
    """Normalize and validate merged config dict into MklistsConfig.

    Args:
        config_dict: Config dictionary as derived from YAML.
        config_rootdir: Root directory of mklists repo.

    Returns:
        Instance of MklistsConfig initialized from config dictionary.

    Note:
        Assumes all required keys are present.
    """
    return MklistsConfig(
        verbose=config_dict["verbose"],
        backup=_make_backup_config(config_dict, config_rootdir),
        routing=_make_routing_config(config_dict, config_rootdir),
        safety=_make_safety_config(config_dict),
        urlify=_make_urlify_config(config_dict, config_rootdir),
    )
