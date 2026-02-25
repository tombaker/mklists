"""Plan of a Mklists execution run.

resolve_execution_context
├── compute run_id (timestamp)
├── decide number of passes
└── produce concrete pass directories
"""

from dataclasses import dataclass
from pathlib import Path
from .config import ConfigContext
from .structure.contexts_datadir import DatadirContext
from .structure.contexts_run import StructuralContext


@dataclass(slots=True)
class ExecutionPass:
    """Execution plan for one pass of a Mklists run."""

    backup_snapshot_dir: Path | None


@dataclass(slots=True)
class ExecutionContext:
    """Execution plan for one Mklists run.

    Note:
        This is a fully resolved execution specification (absolute paths only).
        It includes what must be snapshotted to make the run reproducible.
    """

    datadir_contexts: list[DatadirContext]
    pass_plans: list[ExecutionPass]
    repo_configfile: Path | None
    repo_rulefile: Path | None
    backup_rootdir: Path | None
    backup_depth: int
    routing_dict: dict
    htmldir: Path


def resolve_execution_context(
    *,
    run_context: StructuralContext,
    mklists_cfg: ConfigContext,
    datadir_contexts: list[DatadirContext],
    run_id: str,
) -> ExecutionContext:
    """Construct executable plan for this run.

    Args:
        run_context: Execution context for one Mklists run.
        mklists_cfg: Instance of configuration object ConfigContext.
        datadir_contexts: List of Datadir execution contexts.
        run_id: Timestamp string;.

    Returns:
        ExecutionContext object, holding info needed for execution.

    Note:
        Responsible for resolving relative config paths to absolute.
    """
    config_rootdir = run_context.config_rootdir

    # ----- passes ----------------------------------------------------
    pass_plans: list[ExecutionPass] = []

    if not mklists_cfg.backup.backup_enabled:
        pass_plans.append(ExecutionPass(backup_snapshot_dir=None))
    else:
        pass_count = 1
        if mklists_cfg.routing.routing_enabled and len(datadir_contexts) > 1:
            pass_count = 2

        for i in range(pass_count):
            backup_snapshot_dir = (
                config_rootdir
                / mklists_cfg.backup.backup_rootdir
                / f"{run_id}_{i+1:02d}"
            )
            pass_plans.append(ExecutionPass(backup_snapshot_dir=backup_snapshot_dir))

    # ----- repo-level config -----------------------------------------
    repo_configfile = None
    if run_context.repo_configfile:
        repo_configfile = run_context.repo_configfile

    repo_rulefile = None
    if run_context.repo_rulefile:
        repo_rulefile = run_context.repo_rulefile

    # ----- backup ----------------------------------------------------
    backup_rootdir = None
    backup_depth = 0
    if mklists_cfg.backup.backup_enabled:
        if mklists_cfg.backup.backup_rootdir:
            backup_rootdir = config_rootdir / mklists_cfg.backup.backup_rootdir
            backup_depth = mklists_cfg.backup.backup_depth

    # todo: What iff backup_enabled=True and backup_rootdir=None?

    # ----- routing ---------------------------------------------------
    routing_dict = {}
    if mklists_cfg.routing.routing_enabled:
        routing_dict = mklists_cfg.routing.routing_dict

    # ----- html ------------------------------------------------------
    htmldir = None
    if mklists_cfg.urlify.urlify_enabled:
        htmldir = config_rootdir / mklists_cfg.urlify.urlify_dir

    return ExecutionContext(
        datadir_contexts=datadir_contexts,
        pass_plans=pass_plans,
        repo_configfile=repo_configfile,
        repo_rulefile=repo_rulefile,
        backup_rootdir=backup_rootdir,
        backup_depth=backup_depth,
        routing_dict=routing_dict,
        htmldir=htmldir,
    )
