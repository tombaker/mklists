"""Plan of a Mklists execution run."""

from datetime import datetime, UTC
from mklists.config import Config
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
    config_context: Config,
    run_id: str,
) -> RunPlan:
    """Construct executable plan for this run.

    Args:
        structural_context: Execution context for one Mklists run.
        config_context: Instance of configuration object Config.

    Returns:
        RunPlan object, holding info needed for execution.
    """
    config_rootdir = structural_context.startdir_context.config_rootdir

    # ----- pass plans (backup directories) ---------------------------
    pass_plans = _resolve_pass_plans(
        structural_context=structural_context,
        config_context=config_context,
    )

    # ----- routing ---------------------------------------------------
    routing_dict = {}
    if config_context.routing.routing_enabled:
        routing_dict = config_context.routing.routing_dict

    # ----- repo-level config -----------------------------------------
    repo_configfile = None
    if structural_context.repo_configfile:
        repo_configfile = structural_context.repo_configfile

    repo_rulefile = None
    if structural_context.repo_rulefile:
        repo_rulefile = structural_context.repo_rulefile

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


def _resolve_pass_plans(
    *,
    structural_context: StructuralContext,
    config_context: Config,
) -> list[PassPlan]:
    """Construct executable plan for this run.

    Args:
        structural_context: Execution context for one Mklists run.
        config_context: Instance of configuration object Config.

    Returns:
        List of PassPlan instances.
    """
    config_rootdir = structural_context.startdir_context.config_rootdir
    datadir_contexts = structural_context.datadir_contexts

    # Determine pass count.
    pass_count = 1
    if config_context.routing.routing_enabled and len(datadir_contexts) > 1:
        pass_count = 2

    # Determine snapshot fields (None when backup disabled).
    if not config_context.backup.backup_enabled:
        timestamp = None
        snapshot_repofiles_to_copy = []
    else:
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d_%H%M_%S%f")
        snapshot_repofiles_to_copy = [
            f
            for f in [
                structural_context.startdir_context.repo_configfile_found,
                structural_context.startdir_context.repo_rulefile_found,
            ]
            if f is not None
        ]

    return [
        PassPlan(
            snapshot_dir=(
                config_rootdir
                / config_context.backup.backup_rootdir
                / f"{timestamp}_{i+1:02d}"
                if timestamp
                else None
            ),
            snapshot_repofiles_to_copy=snapshot_repofiles_to_copy,
        )
        for i in range(pass_count)
    ]
