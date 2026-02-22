"""Orchestration of a Mklists execution run."""

from pathlib import Path
from ..config import load_config, MklistsConfig
from ..plan import RunPlan
from .backups import backup_datadirs
from .process_datadirs import process_datadir
from .routing import redistribute_datafiles
from .urlify import urlify_datadirs


def run_mklists(run_plan: RunPlan) -> None:
    """Execute a prepared run plan.

    Args:
        run_plan: Execution plan for a Mklists run.

    Returns:
        None, after executing the run plan.
    """
    datadirs = [ctx.datadir for ctx in run_plan.datadir_contexts]

    for passplan in run_plan.pass_plans:
        if passplan.backup_snapshot_dir is not None:
            backup_datadirs(
                datadirs=datadirs,
                backup_snapshot_dir=passplan.backup_snapshot_dir,
            )

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
                redistribute_datafiles(
                    datadirs=datadirs,
                    routing_dict=run_plan.routing_dict,
                )

    if run_plan.htmldir:
        urlify_datadirs(datadirs=datadirs, htmldir=run_plan.htmldir)
