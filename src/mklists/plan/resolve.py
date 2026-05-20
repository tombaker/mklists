"""Plan of a Mklists execution run."""

from datetime import UTC, datetime

from mklists.config import Config
from mklists.plan.model import (
    BackupPlan,
    DatadirPlan,
    PassPlan,
    RunPlan,
    SkippedDatadir,
)
from mklists.rules.load import load_rules_for_datadir
from mklists.structure.markers import DATATREE_RULEFILE_NAME
from mklists.structure.model import StructuralContext


def resolve_run_plan(
    *,
    structural_context: StructuralContext,
    config: Config,
) -> RunPlan:
    """Construct executable plan for this run.

    Args:
        structural_context: Execution context for one Mklists run.
        config: Instance of configuration object Config.

    Returns:
        RunPlan object, holding info needed for execution.
    """
    # ----- pass plans (backup directories) ---------------------------
    pass_plans = _resolve_pass_plans(
        structural_context=structural_context,
        config=config,
    )

    # ----- linkify ---------------------------------------------------
    linkify_md_dir = config.linkify.linkify_md_dir or None
    linkify_html_dir = config.linkify.linkify_html_dir or None

    # ----- routing ---------------------------------------------------
    routing_dict = {}
    if config.routing.routing_dict:
        routing_dict = config.routing.routing_dict

    # ----- datadir plans ---------------------------------------------
    datadir_plans, skipped_datadirs = _resolve_datadir_plans(
        structural_context=structural_context,
    )

    if config.backup.backup_rootdir:
        backup = BackupPlan(
            backup_rootdir=config.backup.backup_rootdir,
            backup_depth=config.backup.backup_depth,
        )
    else:
        backup = None

    return RunPlan(
        pass_plans=pass_plans,
        datadir_plans=datadir_plans,
        skipped_datadirs=skipped_datadirs,
        routing_dict=routing_dict,
        linkify_md_dir=linkify_md_dir,
        linkify_html_dir=linkify_html_dir,
        is_datatree_root=structural_context.startdir_context.is_datatree_root,
        safety=config.safety,
        backup=backup,
    )


def _resolve_datadir_plans(
    *,
    structural_context: StructuralContext,
) -> tuple[list[DatadirPlan], list[SkippedDatadir]]:
    """Partition datadir contexts into executable plans and skipped datadirs.

    Args:
        structural_context: Execution context for one Mklists run.

    Returns:
        Tuple of (datadir_plans, skipped_datadirs).
    """
    startdir_context = structural_context.startdir_context
    datatree_rulefile = startdir_context.datatree_rulefile_found

    # When running from a datadir-in-datatree, datatree markers live in the
    # parent directory (config_rootdir), not in startdir itself.  resolve_config
    # handles the config file the same way.
    if datatree_rulefile is None and startdir_context.is_datadir_in_datatree:
        candidate = startdir_context.config_rootdir / DATATREE_RULEFILE_NAME
        if candidate.is_file():
            datatree_rulefile = candidate

    datadir_plans: list[DatadirPlan] = []
    skipped_datadirs: list[SkippedDatadir] = []

    for datadir_ctx in structural_context.datadir_contexts:
        if (
            startdir_context.is_datatree_root
            and datadir_ctx.datadir_configfile_found is not None
        ):
            skipped_datadirs.append(
                SkippedDatadir(
                    datadir=datadir_ctx.datadir,
                    datadir_configfile_found=datadir_ctx.datadir_configfile_found,
                )
            )
        else:
            rulefiles_used = [
                f
                for f in [datatree_rulefile, datadir_ctx.datadir_rulefile]
                if f is not None
            ]
            rules = load_rules_for_datadir(rulefiles_used)
            datadir_plans.append(
                DatadirPlan(
                    datadir=datadir_ctx.datadir,
                    rules=rules,
                    rulefiles_used=rulefiles_used,
                )
            )

    return datadir_plans, skipped_datadirs


def _resolve_pass_plans(
    *,
    structural_context: StructuralContext,
    config: Config,
) -> list[PassPlan]:
    """Construct executable plan for this run.

    Args:
        structural_context: Execution context for one Mklists run.
        config: Instance of configuration object Config.

    Returns:
        List of PassPlan instances.
    """
    config_rootdir = structural_context.startdir_context.config_rootdir
    datadir_contexts = structural_context.datadir_contexts

    # Determine pass count.
    pass_count = 1
    if config.routing.routing_dict and len(datadir_contexts) > 1:
        pass_count = 2

    # Determine snapshot fields (None when backup disabled).
    if not config.backup.backup_rootdir:
        timestamp = None
        snapshot_datatree_configfiles = []
    else:
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d_%H%M_%S%f")
        snapshot_datatree_configfiles = [
            f
            for f in [
                structural_context.startdir_context.datatree_configfile_found,
                structural_context.startdir_context.datatree_rulefile_found,
            ]
            if f is not None
        ]

    return [
        PassPlan(
            snapshot_dir=(
                config_rootdir / config.backup.backup_rootdir / f"{timestamp}_{i+1:02d}"
                if timestamp
                else None
            ),
            snapshot_datatree_configfiles=snapshot_datatree_configfiles,
        )
        for i in range(pass_count)
    ]
