"""Orchestration of a Mklists execution run."""

from mklists.plan.model import RunPlan
from mklists.exec.backups import (
    backup_datadirs,
    init_snapshot_dir,
    prune_backupdirs,
)
from mklists.exec.process_datadirs import process_datadir
from mklists.exec.routing import redistribute_datafiles
from mklists.exec.linkify import linkify_datadirs


def run_mklists(run_plan: RunPlan) -> None:
    """Execute a prepared run plan.

    Args:
        run_plan: Execution plan for a Mklists run.

    Returns:
        None, after executing the run plan.
    """
    datadirs = [ctx.datadir for ctx in run_plan.datadir_plans]

    for pass_plan in run_plan.pass_plans:
        if pass_plan.snapshot_dir is not None:

            init_snapshot_dir(
                snapshot_dir=pass_plan.snapshot_dir,
                snapshot_repofiles_to_copy=pass_plan.snapshot_repofiles_to_copy,
            )

            backup_datadirs(
                datadirs=datadirs,
                snapshot_dir=pass_plan.snapshot_dir,
            )

        for datadir_plan in run_plan.datadir_plans:
            process_datadir(
                datadir_plan=datadir_plan,
                safety=run_plan.safety,
            )

        if run_plan.routing_dict:
            redistribute_datafiles(
                datadirs=datadirs,
                routing_dict=run_plan.routing_dict,
            )

    if run_plan.backup is not None:
        prune_backupdirs(
            backup_rootdir=run_plan.backup.backup_rootdir,
            backup_depth=run_plan.backup.backup_depth,
        )

    if run_plan.linkify_dir:
        linkify_datadirs(datadirs=datadirs, linkify_dir=run_plan.linkify_dir)
