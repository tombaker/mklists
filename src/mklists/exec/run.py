"""Orchestration of a Mklists execution run."""

from pathlib import Path
from mklists.config import resolve_config_context, ConfigContext
from mklists.plan.model import RunPlan
from mklists.exec.backups import (
    backup_datadirs,
    init_backup_snapshot_dir,
    prune_backupdirs,
)
from mklists.exec.process_datadirs import process_datadir
from mklists.exec.routing import redistribute_datafiles
from mklists.exec.urlify import urlify_datadirs


def run_mklists(run_plan: RunPlan) -> None:
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

        for datadir_context in run_plan.datadir_contexts:
            config_path = datadir_context.configfile_used

            if config_path not in configs_by_path:
                configs_by_path[config_path] = resolve_config_context(
                    config_rootdir=config_rootdir,
                    configfile_used=config_path,
                )

            config_context = configs_by_path[config_path]

            process_datadir(
                datadir_context=datadir_context,
                config_context=config_context,
            )

            if run_plan.routing_dict:
                redistribute_datafiles(
                    datadirs=datadirs,
                    routing_dict=run_plan.routing_dict,
                )

    if run_plan.htmldir:
        urlify_datadirs(datadirs=datadirs, htmldir=run_plan.htmldir)
