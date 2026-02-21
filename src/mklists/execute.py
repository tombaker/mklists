"""Orchestration of a Mklists execution run."""

from .datadirs import process_datadir
from .plan import RunPlan, PassPlan
from .config import load_config


def run_mklists(run_plan: RunPlan) -> None:
    """Execute a prepared run plan.

    Args:
        run_plan: Execution plan for a Mklists run.

    Returns:
        None, after executing the run plan.
    """
    for passplan in run_plan.pass_plans:
        if passplan.backupdir is not None:
            write_backup(passplan.backupdir)

        configs_by_path: dict[Path | None, MklistsConfig] = {}

        for datadir_ctx in run_plan.datadir_contexts:
            config_path = datadir_ctx.configfile_used

            if config_path not in configs_by_path:
                configs_by_path[config_path] = load_config(configfile_used=config_path)

            mklists_cfg = configs_by_path[config_path]

            process_datadir(
                datadir_ctx=datadir_ctx,
                mklists_cfg=mklists_cfg,
            )

    if run_plan.routing_dict:
        redistribute_datafiles(run_plan.datadir_contexts, run_plan.routing_dict)

    if run_plan.htmldir:
        write_html(run_plan.datadir_contexts, run_plan.htmldir)
