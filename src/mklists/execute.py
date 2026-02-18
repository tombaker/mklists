"""Orchestration of a Mklists execution run."""

from mklists.plan import RunPlan


def run_mklists(run_plan: RunPlan) -> None:
    """Execute a prepared run plan.

    Args:
        run_plan: Execution plan for a Mklists run.

    Returns:
        None, after executing the run plan.
    """
    for passplan in run_plan.passes:
        if passplan.backupdir is not None:
            write_backup(passplan.backupdir)

        for datadir_ctx in run_plan.datadirs:
            process_datadir(datadir_ctx)

    if run_plan.routing_dict:
        redistribute_datafiles(run_plan.datadirs, run_plan.routing_dict)

    if run_plan.htmldir:
        write_html(run_plan.datadirs, run_plan.htmldir)
