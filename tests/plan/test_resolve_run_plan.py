"""Tests $MKLMKL/plan/resolve.py

Tests focus on two decisions resolve_run_plan makes directly:
— routing_dict conditional
- linkify_dir conditional

Also:
- that it returns a RunPlan

Pass-count and snapshot logic are left to test__resolve_pass_plans.py
Datadir partitioning logic is left to test__resolve_datadir_plans.py.
"""

from pathlib import Path
from mklists.config.model import (
    BackupConfig,
    Config,
    LinkifyConfig,
    RoutingConfig,
    SafetyConfig,
)
from mklists.structure.markers import DATADIR_RULEFILE_NAME
from mklists.structure.model import (
    DatadirStructuralContext,
    StartdirStructuralContext,
    StructuralContext,
)
from mklists.plan.model import RunPlan
from mklists.plan.resolve import resolve_run_plan


def make_config(
    *,
    backup_enabled: bool = False,
    routing_enabled: bool = False,
    routing_dict: dict | None = None,
    linkify_enabled: bool = False,
) -> Config:
    """Build a minimal Config for testing resolve_run_plan."""
    return Config(
        verbose=False,
        configfile_used=None,
        config_rootdir=Path("/unused"),
        backup=BackupConfig(
            backup_enabled=backup_enabled,
            backup_rootdir=Path("backups"),
            backup_depth=2,
        ),
        routing=RoutingConfig(
            routing_enabled=routing_enabled,
            routing_dict=routing_dict or {},
        ),
        safety=SafetyConfig(invalid_filename_patterns=[]),
        linkify=LinkifyConfig(
            linkify_enabled=linkify_enabled,
            linkify_dir=Path("markdown"),
        ),
    )


def make_structural_context(
    tmp_path: Path,
    *,
    datadir_rulefile: Path,
) -> StructuralContext:
    """Build a StructuralContext with one normal datadir rooted at tmp_path."""
    return StructuralContext(
        startdir_context=StartdirStructuralContext(
            startdir=tmp_path,
            repo_configfile_found=tmp_path / "mklists.yaml",
            repo_rulefile_found=None,
            datadir_configfile_found=None,
            datadir_rulefile_found=None,
        ),
        datadir_contexts=[
            DatadirStructuralContext(
                datadir=datadir_rulefile.parent,
                datadir_configfile_found=None,
                datadir_rulefile=datadir_rulefile,
            )
        ],
    )


# ----- return type -----------------------------------------------------------


def test_returns_runplan_instance(tmp_path):
    """resolve_run_plan returns a RunPlan."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    plan = resolve_run_plan(
        structural_context=make_structural_context(tmp_path, datadir_rulefile=rulefile),
        config=make_config(),
    )

    assert isinstance(plan, RunPlan)


# ----- routing_dict ----------------------------------------------------------


def test_routing_disabled_routing_dict_is_empty(tmp_path):
    """routing_enabled=False → routing_dict is {} even when config has entries."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    plan = resolve_run_plan(
        structural_context=make_structural_context(tmp_path, datadir_rulefile=rulefile),
        config=make_config(
            routing_enabled=False,
            routing_dict={"to_a.txt": Path("/some/dir")},
        ),
    )

    assert plan.routing_dict == {}


def test_routing_enabled_routing_dict_comes_from_config(tmp_path):
    """routing_enabled=True → routing_dict equals config.routing.routing_dict."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    expected = {"to_a.txt": Path("/some/dir")}
    plan = resolve_run_plan(
        structural_context=make_structural_context(tmp_path, datadir_rulefile=rulefile),
        config=make_config(routing_enabled=True, routing_dict=expected),
    )

    assert plan.routing_dict == expected


# ----- linkify_dir --------------------------------------------------------------


def test_linkify_disabled_linkify_dir_is_none(tmp_path):
    """linkify_enabled=False → linkify_dir is None."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    plan = resolve_run_plan(
        structural_context=make_structural_context(tmp_path, datadir_rulefile=rulefile),
        config=make_config(linkify_enabled=False),
    )

    assert plan.linkify_dir is None


def test_linkify_enabled_linkify_dir_resolves_under_config_rootdir(tmp_path):
    """linkify_enabled=True → linkify_dir is config_rootdir / linkify_dir."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    plan = resolve_run_plan(
        structural_context=make_structural_context(tmp_path, datadir_rulefile=rulefile),
        config=make_config(linkify_enabled=True),
    )

    assert plan.linkify_dir == tmp_path / "markdown"


# ----- backup ----------------------------------------------------------------


def test_backup_disabled_backup_is_none(tmp_path):
    """backup_enabled=False → backup is None."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    plan = resolve_run_plan(
        structural_context=make_structural_context(tmp_path, datadir_rulefile=rulefile),
        config=make_config(backup_enabled=False),
    )

    assert plan.backup is None


def test_backup_enabled_backup_rootdir_comes_from_config(tmp_path):
    """backup_enabled=True → backup.backup_rootdir equals config.backup.backup_rootdir."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    plan = resolve_run_plan(
        structural_context=make_structural_context(tmp_path, datadir_rulefile=rulefile),
        config=make_config(backup_enabled=True),
    )

    assert plan.backup.backup_rootdir == Path("backups")
