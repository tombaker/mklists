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
    backup_rootdir: Path | None = None,
    routing_dict: dict | None = None,
    linkify_md_dir: Path | None = None,
    linkify_html_dir: Path | None = None,
) -> Config:
    """Build a minimal Config for testing resolve_run_plan.

    backup_rootdir=None      → backup disabled
    backup_rootdir=Path      → backup enabled
    routing_dict={}          → routing disabled (empty dict)
    routing_dict={...}       → routing enabled (non-empty dict)
    linkify_md_dir=None      → md linkify disabled
    linkify_md_dir=Path      → md linkify enabled
    linkify_html_dir=None    → html linkify disabled
    linkify_html_dir=Path    → html linkify enabled
    """
    return Config(
        verbose=False,
        configfile_used=None,
        config_rootdir=Path("/unused"),
        backup=BackupConfig(
            backup_rootdir=backup_rootdir,
            backup_depth=2,
        ),
        routing=RoutingConfig(
            routing_dict=routing_dict or {},
        ),
        safety=SafetyConfig(invalid_filename_patterns=[]),
        linkify=LinkifyConfig(
            linkify_md_dir=linkify_md_dir,
            linkify_html_dir=linkify_html_dir,
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
            datatree_configfile_found=tmp_path / "mklists.yaml",
            datatree_rulefile_found=None,
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


def test_routing_dict_empty_routing_dict_is_empty(tmp_path):
    """Empty routing_dict → plan.routing_dict is {}."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    plan = resolve_run_plan(
        structural_context=make_structural_context(tmp_path, datadir_rulefile=rulefile),
        config=make_config(routing_dict={}),
    )

    assert plan.routing_dict == {}


def test_routing_dict_nonempty_routing_dict_comes_from_config(tmp_path):
    """Non-empty routing_dict → plan.routing_dict equals config.routing.routing_dict."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    expected = {"to_a.txt": Path("/some/dir")}
    plan = resolve_run_plan(
        structural_context=make_structural_context(tmp_path, datadir_rulefile=rulefile),
        config=make_config(routing_dict=expected),
    )

    assert plan.routing_dict == expected


# ----- linkify_md_dir / linkify_html_dir ----------------------------------------


def test_linkify_md_dir_none_is_none(tmp_path):
    """linkify_md_dir=None → plan.linkify_md_dir is None."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    plan = resolve_run_plan(
        structural_context=make_structural_context(tmp_path, datadir_rulefile=rulefile),
        config=make_config(linkify_md_dir=None),
    )

    assert plan.linkify_md_dir is None


def test_linkify_md_dir_set_comes_from_config(tmp_path):
    """linkify_md_dir=Path → plan.linkify_md_dir equals config value."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    plan = resolve_run_plan(
        structural_context=make_structural_context(tmp_path, datadir_rulefile=rulefile),
        config=make_config(linkify_md_dir=Path(".linkify")),
    )

    assert plan.linkify_md_dir == Path(".linkify")


def test_linkify_html_dir_none_is_none(tmp_path):
    """linkify_html_dir=None → plan.linkify_html_dir is None."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    plan = resolve_run_plan(
        structural_context=make_structural_context(tmp_path, datadir_rulefile=rulefile),
        config=make_config(linkify_html_dir=None),
    )

    assert plan.linkify_html_dir is None


def test_linkify_html_dir_set_comes_from_config(tmp_path):
    """linkify_html_dir=Path → plan.linkify_html_dir equals config value."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    plan = resolve_run_plan(
        structural_context=make_structural_context(tmp_path, datadir_rulefile=rulefile),
        config=make_config(linkify_html_dir=Path(".linkify_html")),
    )

    assert plan.linkify_html_dir == Path(".linkify_html")


# ----- backup ----------------------------------------------------------------


def test_backup_rootdir_none_backup_is_none(tmp_path):
    """backup_rootdir=None → plan.backup is None."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    plan = resolve_run_plan(
        structural_context=make_structural_context(tmp_path, datadir_rulefile=rulefile),
        config=make_config(backup_rootdir=None),
    )

    assert plan.backup is None


def test_backup_rootdir_set_backup_rootdir_comes_from_config(tmp_path):
    """backup_rootdir=Path("backups") → backup.backup_rootdir equals config value."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    plan = resolve_run_plan(
        structural_context=make_structural_context(tmp_path, datadir_rulefile=rulefile),
        config=make_config(backup_rootdir=Path("backups")),
    )

    assert plan.backup.backup_rootdir == Path("backups")
