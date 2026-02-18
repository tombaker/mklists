"""Plan of a Mklists execution run.

resolve_run_plan
├── compute run_id (timestamp)
├── decide number of passes
└── produce concrete pass directories
"""

from dataclasses import dataclass
import datetime
from pathlib import Path
from .contexts import resolve_datadir_contexts, DatadirContext, RunContext


@dataclass(slots=True)
class PassPlan:
    """Execution plan for one pass of a Mklists run."""

    backupdir: Path | None


@dataclass(slots=True)
class RunPlan:
    """Execution plan for one Mklists run."""

    datadirs: list[DatadirContext]
    passes: list[PassPlan]
    routing_dict: dict
    htmldir: Path


def resolve_run_plan(
    *,
    run_context: RunContext,
    mklists_cfg: MklistsConfig,
    datadir_contexts: list[DatadirContexts],
    run_id: str,
) -> RunPlan:
    """Construct executable plan for this run.

    Args:
        run_context:
        mklists_cfg:
        datadir_contexts:

    Returns:
        RunPlan object, holding info needed for execution.
    """
    rundir = run_context.rundir

    # ----- passes ----------------------------------------------------
    passes: list[PassPlan] = []

    if not mklists_cfg.backup.enabled:
        passes.append(PassPlan(backupdir=None))
    else:
        pass_count = 1
        if mklists_cfg.routing.enabled and len(datadir_contexts) > 1:
            pass_count = 2

        for i in range(pass_count):
            backupdir = rundir / mklists_cfg.backup.directory / f"{run_id}_{i+1:02d}"
            passes.append(PassPlan(backupdir=backupdir))

    # ----- routing ---------------------------------------------------
    routing_dict = {}
    if mklists_cfg.routing.enabled:
        routing_dict = mklists_cfg.routing.map

    # ----- html ------------------------------------------------------
    htmldir = None
    if mklists_cfg.urlify.enabled:
        htmldir = rundir / mklists_cfg.urlify.directory

    return RunPlan(
        datadirs=datadir_contexts,
        passes=passes,
        routing_dict=routing_dict,
        htmldir=htmldir,
    )


def _make_backupdir(backups_rootdir: Path) -> Path:
    """Construct timestamped backup directory path for a mklists execution run.

    Args:
        backups_rootdir: Path of backups tree.
        pass_number: Pass number for this run (1-based).

    Returns:
        Path of backup directory for this pass.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M_%S%f")
    return backups_rootdir / f"{timestamp}_pass{pass_number:02d}"
