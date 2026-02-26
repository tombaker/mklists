"""@@@"""

from dataclasses import dataclass
from pathlib import Path
from mklists.config import ConfigContext
from mklists.rules.model import Rule


@dataclass(slots=True)
class DatadirPlan:
    """Execution-ready context for one datadir."""

    datadir: Path
    rules: list[Rule]
    config_context: ConfigContext


@dataclass(slots=True)
class PassPlan:
    """Execution plan for one pass of a Mklists run."""

    backup_snapshot_dir: Path | None


@dataclass(slots=True)
class RunPlan:
    """Execution-ready context for one Mklists run.

    Note:
        This is a fully resolved execution specification (absolute paths only).
        It includes what must be snapshotted to make the run reproducible.
    """

    datadir_contexts: list[DatadirPlan]
    pass_plans: list[PassPlan]

    repo_configfile: Path | None
    repo_rulefile: Path | None

    backup_rootdir: Path | None
    backup_depth: int

    routing_dict: dict
    htmldir: Path | None
