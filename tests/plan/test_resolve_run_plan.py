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

Test: Function is responsible for resolving relative config paths to absolute.
"""

from pathlib import Path
import pytest
from mklists.config import (
    BackupConfig,
    RoutingConfig,
    SafetyConfig,
    UrlifyConfig,
    ConfigContext,
)
from mklists.structure.contexts_run import RunContext
from mklists.structure.contexts_datadir import DatadirContext
from mklists.plan import PassPlan, RunPlan, resolve_run_plan


def make_cfg(
    *,
    backup_enabled: bool,
    routing_enabled: bool,
    urlify_enabled: bool,
) -> ConfigContext:
    """Fake stand-in makes ConfigContext object by varying just three variables."""
    return ConfigContext(
        verbose=False,
        backup=BackupConfig(
            backup_enabled=backup_enabled,
            backup_rootdir=Path("backups"),  # relative - resolved in plan
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
            urlify_dir=Path("html"),  # relative - resolved in plan
        ),
    )


def test_plan_backups_disabled_one_pass(tmp_path):
    """One Datadir.

    Variables in fake ConfigContext:
        Backups disabled.
        Routing disabled.
        Urlify disabled.

    Expect:
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

    fake_mklists_cfg = make_cfg(
        backup_enabled=False,
        routing_enabled=False,
        urlify_enabled=False,
    )

    actual_run_plan = resolve_run_plan(
        run_context=run_context,
        mklists_cfg=fake_mklists_cfg,
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
        repo_configfile=None,
        repo_rulefile=None,
        backup_rootdir=None,
        backup_depth=0,
        routing_dict={},
        htmldir=None,
    )


def test_plan_backups_enabled_one_pass(tmp_path):
    """One Datadir.

    Variables in fake ConfigContext:
        Backup ENABLED.
        Routing disabled.
        Urlify disabled.

    Expect:
        len(pass_plans) == 1
        pass_plans[0].backup_snapshot_dir is None
    """
    fake_cfg = make_cfg(
        backup_enabled=True,
        routing_enabled=False,
        urlify_enabled=False,
    )

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

    # resolve_run_plan should make backup_root absolute.
    actual_run_plan = resolve_run_plan(
        run_context=run_context,
        mklists_cfg=fake_cfg,
        datadir_contexts=run_context.datadir_contexts,  # from above
        run_id="2026-02-22_12341234",
    )

    assert len(actual_run_plan.pass_plans) == 1

    expected_backup_rootdir = tmp_path / fake_cfg.backup.backup_rootdir
    assert actual_run_plan.backup_rootdir == expected_backup_rootdir

    expected_backup_snapshot_dir = expected_backup_rootdir / "2026-02-22_12341234_01"
    assert (
        actual_run_plan.pass_plans[0].backup_snapshot_dir
        == expected_backup_snapshot_dir
    )

    assert actual_run_plan == RunPlan(
        datadir_contexts=[
            DatadirContext(datadir=Path("/path/to/a"), configfile_used=None, rules=[]),
        ],
        repo_configfile=None,
        repo_rulefile=None,
        backup_rootdir=expected_backup_rootdir,
        backup_depth=2,
        pass_plans=[PassPlan(backup_snapshot_dir=expected_backup_snapshot_dir)],
        routing_dict={},
        htmldir=None,
    )


def test_two_passes_when_routing_multiple(tmp_path):
    """Multiple Datadirs. 

    Variables in fake ConfigContext:
        Backup ENABLED.
        Routing ENABLED.
        Urlify disabled.

    Expect:
        2 passes
        directory created from timestamp
    """
    fake_mklists_cfg = make_cfg(
        backup_enabled=True,
        routing_enabled=True,
        urlify_enabled=False,
    )

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

    plan = resolve_run_plan(
        run_context=run_context,
        mklists_cfg=fake_mklists_cfg,
        datadir_contexts=run_context.datadir_contexts,  # from above
        run_id="T",
    )

    # Expected two passes
    assert len(plan.pass_plans) == 2
    # Expected backupdirs
    assert (
        plan.pass_plans[0].backup_snapshot_dir
        == tmp_path / fake_mklists_cfg.backup.backup_rootdir / "T_01"
    )
    assert (
        plan.pass_plans[1].backup_snapshot_dir
        == tmp_path / fake_mklists_cfg.backup.backup_rootdir / "T_02"
    )


def test_plan_urlify_enabled(tmp_path):
    """Urlify enabled

    Variables in fake ConfigContext:
        Backup disabled.
        Routing disabled.
        Urlify ENABLED.

    Expect: 
        Correct htmldir path.
    """
    fake_mklists_cfg = make_cfg(
        backup_enabled=False,
        routing_enabled=False,
        urlify_enabled=True,
    )

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

    actual_run_plan = resolve_run_plan(
        run_context=run_context,
        mklists_cfg=fake_mklists_cfg,
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
        repo_configfile=None,
        repo_rulefile=None,
        backup_rootdir=None,
        backup_depth=0,
        routing_dict={},
        htmldir=expected_htmldir,  # expected htmldir
    )
