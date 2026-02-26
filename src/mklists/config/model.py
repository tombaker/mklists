"""@@@"""

from typing import Pattern
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class BackupConfig:
    """Settings about backing up data files before processing."""

    backup_enabled: bool
    backup_rootdir: Path
    backup_depth: int


@dataclass(slots=True, frozen=True)
class RoutingConfig:
    """Settings about moving specified files to different destination directories."""

    routing_enabled: bool
    routing_dict: dict[str, Path]


@dataclass(slots=True, frozen=True)
class SafetyConfig:
    """Heuristics for rejecting unsafe filenames for data."""

    invalid_filename_patterns: list[Pattern[str]]


@dataclass(slots=True, frozen=True)
class UrlifyConfig:
    """Settings about writing data files in HTML to a desination directory."""

    urlify_enabled: bool
    urlify_dir: Path


@dataclass(frozen=True, slots=True)
class ConfigContext:
    """Normalized, validated settings for processing one or more datadirs.

    A single config instance is derived from built-in defaults plus an optional
    config file. Multiple datadirs may share the same config instance when they
    share the same effective config file.
    """

    # Provenance
    configfile_used: Path | None
    config_rootdir: Path

    # Settings
    verbose: bool
    backup: BackupConfig
    routing: RoutingConfig
    safety: SafetyConfig
    urlify: UrlifyConfig
