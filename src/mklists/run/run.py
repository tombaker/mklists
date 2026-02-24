"""Orchestration of a Mklists execution run."""

from pathlib import Path
from ..config import resolve_config_context, ConfigContext
from ..plan import ExecutionContext
from .backups import backup_datadirs, init_backup_snapshot_dir, prune_backupdirs
from .process_datadirs import process_datadir
from .routing import redistribute_datafiles
from .urlify import urlify_datadirs


def run_mklists(run_plan: ExecutionContext) -> None:
    """Execute a prepared run plan.

    Args:
        run_plan: Execution plan for a Mklists run.

    Returns:
        None, after executing the run plan.
    """
    datadirs = [ctx.datadir for ctx in run_plan.datadir_contexts]

    for pass_plan in run_plan.pass_plans:
        if pass_plan.backup_snapshot_dir is not None:

            init_backup_snapshot_dir(
                backup_snapshot_dir=pass_plan.backup_snapshot_dir,
                repo_configfile=run_plan.repo_configfile,
                repo_rulefile=run_plan.repo_rulefile,
            )

            backup_datadirs(
                datadirs=datadirs,
                backup_snapshot_dir=pass_plan.backup_snapshot_dir,
            )

            if run_plan.backup_rootdir is not None:
                prune_backupdirs(
                    backup_rootdir=run_plan.backup_rootdir,
                    backup_depth=run_plan.backup_depth,
                )


        configs_by_path: dict[Path | None, ConfigContext] = {}

        for datadir_ctx in run_plan.datadir_contexts:
            config_path = datadir_ctx.configfile_used

            if config_path not in configs_by_path:
                configs_by_path[config_path] = resolve_config_context(configfile_used=config_path)

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
