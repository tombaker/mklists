"""Plan of a Mklists execution run.

resolve_run_plan
├── compute run_id (timestamp)
├── decide number of passes
└── produce concrete pass directories
"""

from dataclasses import dataclass
import datetime
from pathlib import Path
from .config import MklistsConfig
from .contexts import DatadirContext, RunContext


@dataclass(slots=True)
class PassPlan:
    """Execution plan for one pass of a Mklists run."""

    backupdir: Path | None


@dataclass(slots=True)
class RunPlan:
    """Execution plan for one Mklists run."""

    datadir_contexts: list[DatadirContext]
    pass_plans: list[PassPlan]
    routing_dict: dict
    htmldir: Path


def resolve_run_plan(
    *,
    run_context: RunContext,
    mklists_cfg: MklistsConfig,
    datadir_contexts: list[DatadirContext],
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
    pass_plans: list[PassPlan] = []

    if not mklists_cfg.backup.enabled:
        pass_plans.append(PassPlan(backupdir=None))
    else:
        pass_count = 1
        if mklists_cfg.routing.enabled and len(datadir_contexts) > 1:
            pass_count = 2

        for i in range(pass_count):
            backupdir = rundir / mklists_cfg.backup.directory / f"{run_id}_{i+1:02d}"
            pass_plans.append(PassPlan(backupdir=backupdir))

    # ----- routing ---------------------------------------------------
    routing_dict = {}
    if mklists_cfg.routing.enabled:
        routing_dict = mklists_cfg.routing.map

    # ----- html ------------------------------------------------------
    htmldir = None
    if mklists_cfg.urlify.enabled:
        htmldir = rundir / mklists_cfg.urlify.directory

    return RunPlan(
        datadir_contexts=datadir_contexts,
        pass_plans=pass_plans,
        routing_dict=routing_dict,
        htmldir=htmldir,
    )
