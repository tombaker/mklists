"""Tests $MKLMKL/plan.py

3. Backups enabled, routing enabled, ONE datadir
   Expect:
        1 pass

4. Backups enabled, routing enabled, MULTIPLE datadirs
   Expect:
        2 passes

5. Routing disabled
   Expect:
        routing_dict is empty

6. Urlify disabled
   Expect:
        htmldir is None

7. Urlify enabled
   Expect:
        correct htmldir path

Real DatadirContext objects not needed; simple list-like stubs will do.
Planner only checks: `len(datadir_contexts)`.

Real filesystem not needed. Rather, tiny factories:
- fake_run_context
- fake_config
- fake_datadir_contexts
"""

import pytest
from mklists.config import (
    BackupConfig,
    RoutingConfig,
    SafetyConfig,
    UrlifyConfig,
    MklistsConfig,
)
from mklists.structure.contexts_run import RunContext
from mklists.structure.contexts_datadir import DatadirContext
from mklists.plan import resolve_run_plan


def make_cfg(
    *,
    backup_enabled: bool,
    routing_enabled: bool,
    urlify_enabled: bool,
    tmp_path: Path,
) -> MklistsConfig:
    return MklistsConfig(
        verbose=False,
        backup=BackupConfig(
            backup_enabled=backup_enabled,
            backup_dir=tmp_path / "backups",
            backup_depth=2,
        ),
        routing=RoutingConfig(
            routing_enabled=routing_enabled,
            routing_dict={},
        ),
        safety=SafetyConfig(
            invalid_filename_patterns=[],
        ),
        urlify=UrlifyConfig(
            urlify_enabled=urlify_enabled,
            urlify_dir=tmp_path / "html",
        ),
    )


def test_plan_backups_disabled(tmp_path, monkeypatch):
    """Backups disabled - expect:

        len(pass_plans) == 1
        pass_plans[0].backupdir is None
    """
    run_context = RunContext(
        config_rootdir=tmp_path,
        repo_configfile=None,
        repo_rulefile=None,
        datadir_contexts=[
            DatadirContext(
                datadir=tmp_path / "a",
                configfile_used=None,
                rules=[],
            ),
        ],
    )

    cfg = make_cfg(
        backup_enabled=False,
        routing_enabled=False,
        urlify_enabled=False,
        tmp_path=tmp_path,
    )

    run_plan = resolve_run_plan(
        run_context=run_context,
        mklists_cfg=cfg,
        datadir_contexts=[object()],
        run_id="2026-02-22_12341234",
    )

    assert len(run_plan.pass_plans) == 1
    assert run_plan.pass_plans[0].backupdir is None

# @dataclass(slots=True)
# class PassPlan:
#     """Execution plan for one pass of a Mklists run."""
# 
#     backupdir: Path | None
# 
# @dataclass(slots=True)
# class RunPlan:
#     """Execution plan for one Mklists run."""
# 
#     datadir_contexts: list[DatadirContext]
#     pass_plans: list[PassPlan]
#     routing_dict: dict
#     htmldir: Path


@pytest.mark.skip
def test_two_passes_when_routing_multiple(tmp_path, monkeypatch):
    """Backups enabled, routing disabled - expect:

        1 pass
        directory created from timestamp
    """
    monkeypatch.setattr("mklists.plan.make_timestamp", lambda: "T")

    run_context = RunContext(
        config_rootdir=tmp_path,
        repo_configfile=None,
        repo_rulefile=None,
        datadirs=[tmp_path / "a", tmp_path / "b"],
    )

    cfg = make_cfg(
        backup_enabled=True,
        routing_enabled=True,
        urlify_enabled=False,
    )

    plan = resolve_run_plan(
        run_context=run_context,
        mklists_cfg=cfg,
        datadir_contexts=[object(), object()],
    )

    assert len(plan.pass_plans) == 2
    assert plan.pass_plans[0].backupdir == tmp_path / cfg.backup.directory / "T_01"
    assert plan.pass_plans[1].backupdir == tmp_path / cfg.backup.directory / "T_02"
