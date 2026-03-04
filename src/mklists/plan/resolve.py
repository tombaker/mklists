"""Plan of a Mklists execution run."""

from datetime import datetime, UTC
from mklists.config import ConfigContext
from mklists.structure.model import (
    DatadirStructuralContext, 
    StartdirStructuralContext, 
    StructuralContext,
)
from mklists.plan.model import (
    DatadirPlan,
    PassPlan, 
    SkippedDatadir,
    RunPlan,
)


def resolve_run_plan(
    *,
    structural_context: StructuralContext,
    config_context: ConfigContext,
    run_id: str,
) -> RunPlan:
    """Construct executable plan for this run.

    Args:
        structural_context: Execution context for one Mklists run.
        config_context: Instance of configuration object ConfigContext.
        run_id: Timestamp string;.

    Returns:
        RunPlan object, holding info needed for execution.

    Note:
        Responsible for resolving relative config paths to absolute.
    """
    config_rootdir = structural_context.config_rootdir

    # ----- passes ----------------------------------------------------

    pass_plans = _resolve_pass_plans(
        structural_context=structural_context,
        config_context=config_context,
    )

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
        pass_plans=pass_plans,
        datadir_plans=datadir_plans,
        skipped_datadirs=skipped_datadirs,
        routing_dict=routing_dict,
        htmldir=htmldir,
    )


TIMESTAMP = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")


def _resolve_pass_plans(
    *,
    structural_context: StructuralContext,
    config_context: ConfigContext,
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

    pass_plans: list[PassPlan] = []

    if not config_context.backup.backup_enabled:
        pass_plans.append(
            PassPlan(
                snapshot_dir=None,
                snapshot_repofiles_to_copy=[],
            )
        )
    else:
        pass_count = 1
        if config_context.routing.routing_enabled and len(datadir_contexts) > 1:
            pass_count = 2

        for i in range(pass_count):
            snapshot_dir = (
                config_rootdir
                / config_context.backup.backup_rootdir
                / f"{TIMESTAMP}_{i+1:02d}"
            )

            snapshot_repofiles_to_copy = []
            repo_configfile_found = (
                structural_context.startdir_context.repo_configfile_found
            )
            if repo_configfile_found:
                snapshot_repofiles_to_copy.append(repo_configfile_found)

            repo_rulefile_found = (
                structural_context.startdir_context.repo_rulefile_found
            )
            if repo_rulefile_found:
                snapshot_repofiles_to_copy.append(repo_rulefile_found)

            pass_plans.append(
                PassPlan(
                    snapshot_dir=snapshot_dir,
                    snapshot_repofiles_to_copy=snapshot_repofiles_to_copy,
                )
            )

    return pass_plans

