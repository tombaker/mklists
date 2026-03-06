"""Resolved features for executing a Mklists run."""

from dataclasses import dataclass
from pathlib import Path
from mklists.config.model import SafetyConfig
from mklists.rules.model import Rule


@dataclass(frozen=True, slots=True)
class DatadirPlan:
    """Execution plan for one datadir."""

    datadir: Path
    rules: list[Rule]
    rulefiles_used: list[Path]


@dataclass(frozen=True, slots=True)
class PassPlan:
    """Execution plan for one pass of a Mklists run."""

    snapshot_dir: Path | None
    snapshot_repofiles_to_copy: list[Path]


@dataclass(frozen=True, slots=True)
class SkippedDatadir:
    """Metadata about datadirs in execution scope that are marked as self-contained."""

    datadir: Path
    datadir_configfile_found: Path


@dataclass(frozen=True, slots=True)
class BackupPlan:
    """Backup parameters for one Mklists run."""

    backup_rootdir: Path
    backup_depth: int


@dataclass(frozen=True, slots=True)
class RunPlan:
    """Execution plan for one Mklists run."""

    pass_plans: list[PassPlan]
    datadir_plans: list[DatadirPlan]
    skipped_datadirs: list[SkippedDatadir]
    routing_dict: dict
    linkify_dir: Path | None
    safety: SafetyConfig
    backup: BackupPlan | None
