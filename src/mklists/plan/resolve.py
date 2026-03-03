"""Plan of a Mklists execution run.

resolve_run_plan
├── compute run_id (timestamp)
├── decide number of passes
└── produce concrete pass directories
"""

from mklists.config import ConfigContext
from mklists.structure.model import DatadirStructuralContext, StructuralContext
from mklists.plan.model import PassPlan, RunPlan


def resolve_run_plan(
    *,
    structural_context: StructuralContext,
    config_context: ConfigContext,
    datadir_contexts: list[DatadirStructuralContext],
    run_id: str,
) -> RunPlan:
    """Construct executable plan for this run.

    Args:
        structural_context: Execution context for one Mklists run.
        config_context: Instance of configuration object ConfigContext.
        datadir_contexts: List of Datadir execution contexts.
        run_id: Timestamp string;.

    Returns:
        RunPlan object, holding info needed for execution.

    Note:
        Responsible for resolving relative config paths to absolute.
    """
    config_rootdir = structural_context.config_rootdir

    # ----- passes ----------------------------------------------------
    pass_plans: list[PassPlan] = []

    if not config_context.backup.backup_enabled:
        pass_plans.append(PassPlan(backup_snapshot_dir=None))
    else:
        pass_count = 1
        if config_context.routing.routing_enabled and len(datadir_contexts) > 1:
            pass_count = 2

        for i in range(pass_count):
            backup_snapshot_dir = (
                config_rootdir
                / config_context.backup.backup_rootdir
                / f"{run_id}_{i+1:02d}"
            )
            pass_plans.append(PassPlan(backup_snapshot_dir=backup_snapshot_dir))

    # ----- repo-level config -----------------------------------------
    repo_configfile = None
    if structural_context.repo_configfile:
        repo_configfile = structural_context.repo_configfile

    repo_rulefile = None
    if structural_context.repo_rulefile:
        repo_rulefile = structural_context.repo_rulefile

    # ----- backup ----------------------------------------------------
    backup_rootdir = None
    backup_depth = 0
    if config_context.backup.backup_enabled:
        if config_context.backup.backup_rootdir:
            backup_rootdir = config_rootdir / config_context.backup.backup_rootdir
            backup_depth = config_context.backup.backup_depth

    # ----- routing ---------------------------------------------------
    routing_dict = {}
    if config_context.routing.routing_enabled:
        routing_dict = config_context.routing.routing_dict

    # ----- html ------------------------------------------------------
    htmldir = None
    if config_context.linkify.html_enabled:
        htmldir = config_rootdir / config_context.linkify.htmldir

    return RunPlan(
        datadir_contexts=datadir_contexts,
        pass_plans=pass_plans,
        repo_configfile=repo_configfile,
        repo_rulefile=repo_rulefile,
        backup_rootdir=backup_rootdir,
        backup_depth=backup_depth,
        routing_dict=routing_dict,
        htmldir=htmldir,
    )
