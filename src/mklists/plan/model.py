"""Resolved features for executing a Mklists run."""

from dataclasses import dataclass
from pathlib import Path
from mklists.config import ConfigContext
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
    repo_configfile_found: Path | None
    repo_rulefile_found: Path | None


@dataclass(frozen=True, slots=True)
class SkippedDatadir:
    """Metadata about datadirs in execution scope that are marked as self-contained."""

    datadir: Path
    datadir_configfile_found: Path


@dataclass(frozen=True, slots=True)
class RunPlan:
    """Execution plan for one Mklists run."""

    pass_plans: list[PassPlan]
    datadir_plans: list[DatadirPlan]
    skipped_datadirs: list[SkippedDatadirPlan]
    routing_dict: dict
    htmldir: Path | None
