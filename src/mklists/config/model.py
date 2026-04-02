"""@@@"""

from typing import Pattern
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class BackupConfig:
    """Settings about backing up data files before processing."""

    backup_rootdir: Path | None
    backup_depth: int


@dataclass(slots=True, frozen=True)
class RoutingConfig:
    """Settings about moving specified files to different destination directories."""

    routing_dict: dict[str, Path]


@dataclass(slots=True, frozen=True)
class SafetyConfig:
    """Heuristics for rejecting unsafe filenames for data."""

    invalid_filename_patterns: list[Pattern[str]]


@dataclass(slots=True, frozen=True)
class LinkifyConfig:
    """Settings about writing data files to browsable mirror directories."""

    linkify_md_dir: Path | None
    linkify_html_dir: Path | None


@dataclass(frozen=True, slots=True)
class Config:
    """Normalized, validated settings for processing one or more datadirs."""

    # Provenance
    configfile_used: Path | None
    config_rootdir: Path

    # Settings
    verbose: bool
    backup: BackupConfig
    linkify: LinkifyConfig
    routing: RoutingConfig
    safety: SafetyConfig
