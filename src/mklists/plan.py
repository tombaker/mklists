"""Plan of a Mklists execution run.

resolve_run_plan
├── compute run_id (timestamp)
├── decide number of passes
└── produce concrete pass directories
"""

from dataclasses import dataclass
from pathlib import Path
from .config import MklistsConfig
from .structure.contexts_datadir import DatadirContext
from .structure.contexts_run import RunContext


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
    config_rootdir = run_context.config_rootdir

    # ----- passes ----------------------------------------------------
    pass_plans: list[PassPlan] = []

    if not mklists_cfg.backup.backup_enabled:
        pass_plans.append(PassPlan(backupdir=None))
    else:
        pass_count = 1
        if mklists_cfg.routing.routing_enabled and len(datadir_contexts) > 1:
            pass_count = 2

        for i in range(pass_count):
            backupdir = (
                config_rootdir / mklists_cfg.backup.backup_dir / f"{run_id}_{i+1:02d}"
            )
            pass_plans.append(PassPlan(backupdir=backupdir))

    # ----- routing ---------------------------------------------------
    routing_dict = {}
    if mklists_cfg.routing.routing_enabled:
        routing_dict = mklists_cfg.routing.routing_dict

    # ----- html ------------------------------------------------------
    htmldir = None
    if mklists_cfg.urlify.urlify_enabled:
        htmldir = config_rootdir / mklists_cfg.urlify.urlify_dir

    return RunPlan(
        datadir_contexts=datadir_contexts,
        pass_plans=pass_plans,
        routing_dict=routing_dict,
        htmldir=htmldir,
    )
