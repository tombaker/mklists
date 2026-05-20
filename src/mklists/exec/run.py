"""Orchestration of a Mklists execution run."""

from pathlib import Path

from mklists.errors import DataNotFoundError
from mklists.exec.backups import (
    backup_datadirs,
    init_snapshot_dir,
    prune_backupdirs,
)
from mklists.exec.linkify import linkify_html_datadirs, linkify_md_datadirs
from mklists.exec.process_datadirs import process_datadir
from mklists.exec.routing import redistribute_datafiles
from mklists.logging import logger
from mklists.plan.model import RunPlan


def run_mklists(run_plan: RunPlan) -> list[Path]:
    """Execute a prepared run plan.

    Args:
        run_plan: Execution plan for a Mklists run.

    Returns:
        List of datadir paths that were skipped because they contained no data.
    """
    datadirs = [ctx.datadir for ctx in run_plan.datadir_plans]
    empty_datadirs: list[Path] = []

    total_passes = len(run_plan.pass_plans)
    for pass_number, pass_plan in enumerate(run_plan.pass_plans, start=1):
        if pass_plan.snapshot_dir is not None:

            init_snapshot_dir(
                snapshot_dir=pass_plan.snapshot_dir,
                snapshot_datatree_configfiles=pass_plan.snapshot_datatree_configfiles,
            )

            backup_datadirs(
                datadirs=datadirs,
                snapshot_dir=pass_plan.snapshot_dir,
            )

        for datadir_plan in run_plan.datadir_plans:
            logger.info(str(datadir_plan.datadir))
            try:
                process_datadir(
                    datadir_plan=datadir_plan,
                    safety=run_plan.safety,
                )
            except DataNotFoundError as exc:
                if run_plan.is_datatree_root:
                    empty_datadirs.append(datadir_plan.datadir)
                else:
                    raise DataNotFoundError(
                        f"No data found in {datadir_plan.datadir}"
                    ) from exc

        if run_plan.routing_dict:
            redistribute_datafiles(
                datadirs=datadirs,
                routing_dict=run_plan.routing_dict,
            )

        logger.info(f"Completed pass {pass_number} out of {total_passes}")

    if run_plan.backup is not None:
        prune_backupdirs(
            backup_rootdir=run_plan.backup.backup_rootdir,
            backup_depth=run_plan.backup.backup_depth,
        )

    if run_plan.linkify_md_dir or run_plan.linkify_html_dir:
        _run_linkify(run_plan=run_plan, datadirs=datadirs)

    return empty_datadirs


def _run_linkify(*, run_plan: RunPlan, datadirs: list[Path]) -> None:
    if not run_plan.is_datatree_root:
        logger.info("Skip linkify because run directory is not datatree root")
        return
    if run_plan.linkify_md_dir:
        linkify_md_datadirs(datadirs=datadirs, linkify_md_dir=run_plan.linkify_md_dir)
    if run_plan.linkify_html_dir:
        linkify_html_datadirs(datadirs=datadirs, linkify_html_dir=run_plan.linkify_html_dir)
