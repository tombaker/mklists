"""Orchestration of a Mklists execution run."""

from pathlib import Path
import shutil
from typing import Iterable
from .datadirs import process_datadir
from .plan import RunPlan, PassPlan
from .config import load_config, MklistsConfig


def run_mklists(run_plan: RunPlan) -> None:
    """Execute a prepared run plan.

    Args:
        run_plan: Execution plan for a Mklists run.

    Returns:
        None, after executing the run plan.
    """
    datadirs = [ctx.datadir for ctx in run_plan.datadir_contexts]

    for passplan in run_plan.pass_plans:
        if passplan.backupdir is not None:
            _backup_datadirs(
                datadirs=datadirs,
                pass_backup_root=passplan.backupdir,
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
                _redistribute_datafiles(run_plan.routing_dict)

    if run_plan.htmldir:
        _urlify_datadirs(
            datadirs=datadirs,
            htmldir=run_plan.htmldir
        )

def _urlify_datadirs():
    pass

def _redistribute_datafiles(routing_dict):
    pass
