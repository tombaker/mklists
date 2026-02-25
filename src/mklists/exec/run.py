"""Orchestration of a Mklists execution run."""

from pathlib import Path
from mklists.config import resolve_config_context, ConfigContext
from mklists.execution.execution_context import ExecutionPlan
from mklists.exec.backups import backup_datadirs, init_backup_snapshot_dir, prune_backupdirs
from mklists.exec.process_datadirs import process_datadir
from mklists.exec.routing import redistribute_datafiles
from mklists.exec.urlify import urlify_datadirs


def run_mklists(execution_context: ExecutionPlan) -> None:
    """Execute a prepared run plan.

    Args:
        execution_context: Execution plan for a Mklists run.

    Returns:
        None, after executing the run plan.
    """
    datadirs = [ctx.datadir for ctx in execution_context.datadir_contexts]

    for pass_plan in execution_context.pass_plans:
        if pass_plan.backup_snapshot_dir is not None:

            init_backup_snapshot_dir(
                backup_snapshot_dir=pass_plan.backup_snapshot_dir,
                repo_configfile=execution_context.repo_configfile,
                repo_rulefile=execution_context.repo_rulefile,
            )

            backup_datadirs(
                datadirs=datadirs,
                backup_snapshot_dir=pass_plan.backup_snapshot_dir,
            )

            if execution_context.backup_rootdir is not None:
                prune_backupdirs(
                    backup_rootdir=execution_context.backup_rootdir,
                    backup_depth=execution_context.backup_depth,
                )

        configs_by_path: dict[Path | None, ConfigContext] = {}

        for datadir_ctx in execution_context.datadir_contexts:
            config_path = datadir_ctx.configfile_used

            if config_path not in configs_by_path:
                configs_by_path[config_path] = resolve_config_context(
                    configfile_used=config_path
                )

            mklists_cfg = configs_by_path[config_path]

            process_datadir(
                datadir_ctx=datadir_ctx,
                mklists_cfg=mklists_cfg,
            )

            if execution_context.routing_dict:
                redistribute_datafiles(
                    datadirs=datadirs,
                    routing_dict=execution_context.routing_dict,
                )

    if execution_context.htmldir:
        urlify_datadirs(datadirs=datadirs, htmldir=execution_context.htmldir)
