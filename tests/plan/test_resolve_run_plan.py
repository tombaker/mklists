"""Tests $MKLMKL/plan.py

5. Routing disabled
   Expect:
        routing_dict is empty

6. Urlify disabled
   Expect:
        htmldir is None

7. Urlify enabled
   Expect:
        correct htmldir path

Real filesystem not needed. Rather, tiny factories:
- fake_run_context
- fake_config
- fake_datadir_contexts
"""

from pathlib import Path
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
from mklists.plan import PassPlan, RunPlan, resolve_run_plan


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
            backup_rootdir=tmp_path / "backups",
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


def test_plan_backups_disabled_one_pass(tmp_path):
    """Backups disabled - expect:

    len(pass_plans) == 1
    pass_plans[0].backup_snapshot_dir is None
    """
    run_context = RunContext(
        config_rootdir=tmp_path,
        repo_configfile=None,
        repo_rulefile=None,
        datadir_contexts=[
            DatadirContext(
                datadir=Path("/path/to/a"),
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

    actual_run_plan = resolve_run_plan(
        run_context=run_context,
        mklists_cfg=cfg,
        datadir_contexts=run_context.datadir_contexts,
        run_id="2026-02-22_12341234",
    )

    assert len(actual_run_plan.pass_plans) == 1
    assert actual_run_plan.pass_plans[0].backup_snapshot_dir is None
    assert actual_run_plan == RunPlan(
        datadir_contexts=[
            DatadirContext(datadir=Path("/path/to/a"), configfile_used=None, rules=[]),
        ],
        pass_plans=[PassPlan(backup_snapshot_dir=None)],
        routing_dict={},
        htmldir=None,
    )


def test_plan_backups_enabled_one_pass(tmp_path):
    """Backups enabled, routing disabled, one datadir - expect:

    len(pass_plans) == 1
    pass_plans[0].backup_snapshot_dir is None
    """
    run_context = RunContext(
        config_rootdir=tmp_path,
        repo_configfile=None,
        repo_rulefile=None,
        datadir_contexts=[
            DatadirContext(
                datadir=Path("/path/to/a"),
                configfile_used=None,
                rules=[],
            ),
        ],
    )

    cfg = make_cfg(
        backup_enabled=True,
        routing_enabled=False,
        urlify_enabled=False,
        tmp_path=tmp_path,
    )

    actual_run_plan = resolve_run_plan(
        run_context=run_context,
        mklists_cfg=cfg,
        datadir_contexts=run_context.datadir_contexts,  # from above
        run_id="2026-02-22_12341234",
    )

    expected_backupdir = tmp_path / cfg.backup.backup_rootdir / "2026-02-22_12341234_01"

    assert len(actual_run_plan.pass_plans) == 1
    assert actual_run_plan.pass_plans[0].backup_snapshot_dir == expected_backupdir
    assert actual_run_plan == RunPlan(
        datadir_contexts=[
            DatadirContext(datadir=Path("/path/to/a"), configfile_used=None, rules=[]),
        ],
        pass_plans=[PassPlan(backup_snapshot_dir=expected_backupdir)],
        routing_dict={},
        htmldir=None,
    )


def test_two_passes_when_routing_multiple(tmp_path):
    """Backups enabled, routing enabled, MULTIPLE datadirs - expect:
    2 passes
    directory created from timestamp
    """
    run_context = RunContext(
        config_rootdir=tmp_path,
        repo_configfile=None,
        repo_rulefile=None,
        datadir_contexts=[
            DatadirContext(
                datadir=Path("/path/to/a"),
                configfile_used=None,
                rules=[],
            ),
            DatadirContext(
                datadir=Path("/path/to/b"),
                configfile_used=None,
                rules=[],
            ),
        ],
    )

    cfg = make_cfg(
        backup_enabled=True,
        routing_enabled=True,
        urlify_enabled=False,
        tmp_path=tmp_path,
    )

    plan = resolve_run_plan(
        run_context=run_context,
        mklists_cfg=cfg,
        datadir_contexts=run_context.datadir_contexts,  # from above
        run_id="T",
    )

    # Expected two passes
    assert len(plan.pass_plans) == 2
    # Expected backupdirs
    assert (
        plan.pass_plans[0].backup_snapshot_dir
        == tmp_path / cfg.backup.backup_rootdir / "T_01"
    )
    assert (
        plan.pass_plans[1].backup_snapshot_dir
        == tmp_path / cfg.backup.backup_rootdir / "T_02"
    )


def test_plan_urlify_enabled(tmp_path):
    """Urlify enabled - expect correct htmldir path."""
    run_context = RunContext(
        config_rootdir=tmp_path,
        repo_configfile=None,
        repo_rulefile=None,
        datadir_contexts=[
            DatadirContext(
                datadir=Path("/path/to/a"),
                configfile_used=None,
                rules=[],
            ),
        ],
    )

    # Urlify enabled
    cfg = make_cfg(
        backup_enabled=False,
        routing_enabled=False,
        urlify_enabled=True,
        tmp_path=tmp_path,
    )

    actual_run_plan = resolve_run_plan(
        run_context=run_context,
        mklists_cfg=cfg,
        datadir_contexts=run_context.datadir_contexts,  # from above
        run_id="2026-02-22_12341234",
    )

    # Expected htmldir
    expected_htmldir = tmp_path / "html"

    assert len(actual_run_plan.pass_plans) == 1
    assert actual_run_plan == RunPlan(
        datadir_contexts=[
            DatadirContext(datadir=Path("/path/to/a"), configfile_used=None, rules=[]),
        ],
        pass_plans=[PassPlan(backup_snapshot_dir=None)],
        routing_dict={},
        htmldir=expected_htmldir,  # expected htmldir
    )
