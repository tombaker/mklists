"""Tests $MKLMKL/plan/resolve.py: _resolve_pass_plans."""

from pathlib import Path
from mklists.config.model import (
    BackupConfig,
    ConfigContext,
    LinkifyConfig,
    RoutingConfig,
    SafetyConfig,
)
from mklists.structure.model import (
    DatadirStructuralContext,
    StartdirStructuralContext,
    StructuralContext,
)
from mklists.plan.model import PassPlan
from mklists.plan.resolve import _resolve_pass_plans


def fake_make_config_context(
    *,
    backup_enabled: bool,
    routing_enabled: bool = False,
) -> ConfigContext:
    """Fake stand-in makes ConfigContext object by varying key variables."""
    return ConfigContext(
        verbose=False,
        configfile_used=Path("foo"),
        config_rootdir=Path("bar"),
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
        linkify=LinkifyConfig(
            html_enabled=False,
            html_dir=Path("html"),
        ),
    )


def fake_make_structural_context(
    tmp_path: Path,
    *,
    num_datadirs: int = 1,
    repo_configfile_found: Path | None = None,
    repo_rulefile_found: Path | None = None,
) -> StructuralContext:
    """Creates a StructuralContext with a valid config_rootdir.

    Note:
        Defaults to repo_configfile_found=tmp_path/"mklists.yaml" so that
        is_repo_root=True and config_rootdir=tmp_path (the startdir).

        Pass explicit repo_configfile_found=None only when repo_rulefile_found
        is set (still gives is_repo_root=True).
    """
    if repo_configfile_found is None and repo_rulefile_found is None:
        repo_configfile_found = tmp_path / "mklists.yaml"

    return StructuralContext(
        startdir_context=StartdirStructuralContext(
            startdir=tmp_path,
            repo_configfile_found=repo_configfile_found,
            repo_rulefile_found=repo_rulefile_found,
            datadir_configfile_found=None,
            datadir_rulefile_found=None,
        ),
        datadir_contexts=[
            DatadirStructuralContext(
                datadir=tmp_path / f"dir{i}",
                datadir_configfile_found=None,
                datadir_rulefile=tmp_path / f"dir{i}/.rules",
            )
            for i in range(num_datadirs)
        ],
    )


# ----- backup disabled -------------------------------------------------------

def test_backup_disabled_returns_one_pass(tmp_path):
    """When backups disabled: one pass."""
    sc = fake_make_structural_context(tmp_path)
    cc = fake_make_config_context(backup_enabled=False)
    result = _resolve_pass_plans(structural_context=sc, config_context=cc)
    assert result == [
        PassPlan(
            snapshot_dir=None, 
            snapshot_repofiles_to_copy=[]
        )
    ]
    assert len(result) == 1


# ----- pass count ------------------------------------------------------------

def test_backup_enabled_routing_disabled_returns_one_pass(tmp_path):
    """When backups enabled and one datadir: one pass."""
    sc = fake_make_structural_context(tmp_path)
    cc = fake_make_config_context(backup_enabled=True, routing_enabled=False)
    result = _resolve_pass_plans(structural_context=sc, config_context=cc)
    assert len(result) == 1


def test_routing_enabled_single_datadir_returns_one_pass(tmp_path):
    """Routing enabled but only one datadir: still one pass."""
    sc = fake_make_structural_context(tmp_path, num_datadirs=1)
    cc = fake_make_config_context(backup_enabled=True, routing_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config_context=cc)
    assert len(result) == 1


def test_routing_enabled_multiple_datadirs_returns_two_passes(tmp_path):
    sc = fake_make_structural_context(tmp_path, num_datadirs=2)
    cc = fake_make_config_context(backup_enabled=True, routing_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config_context=cc)
    assert len(result) == 2


# ----- snapshot_dir paths ----------------------------------------------------

def test_snapshot_dir_is_under_config_rootdir_and_backup_rootdir(tmp_path):
    sc = fake_make_structural_context(tmp_path)
    cc = fake_make_config_context(backup_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config_context=cc)
    # config_rootdir=tmp_path (is_repo_root=True), backup_rootdir="backups"
    assert result[0].snapshot_dir.parent == tmp_path / "backups"


def test_single_pass_snapshot_dir_name_ends_with_01(tmp_path):
    sc = fake_make_structural_context(tmp_path)
    cc = fake_make_config_context(backup_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config_context=cc)
    assert result[0].snapshot_dir.name.endswith("_01")


def test_two_passes_have_01_and_02_suffixes(tmp_path):
    sc = fake_make_structural_context(tmp_path, num_datadirs=2)
    cc = fake_make_config_context(backup_enabled=True, routing_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config_context=cc)
    assert result[0].snapshot_dir.name.endswith("_01")
    assert result[1].snapshot_dir.name.endswith("_02")


def test_two_passes_share_same_timestamp(tmp_path):
    """Both snapshot dirs differ only in suffix, proving one timestamp was used."""
    sc = fake_make_structural_context(tmp_path, num_datadirs=2)
    cc = fake_make_config_context(backup_enabled=True, routing_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config_context=cc)
    assert result[0].snapshot_dir.parent == result[1].snapshot_dir.parent


# ----- snapshot_repofiles_to_copy --------------------------------------------

def test_repo_configfile_included_in_snapshot_repofiles(tmp_path):
    repo_cfg = tmp_path / "mklists.yaml"
    sc = fake_make_structural_context(tmp_path, repo_configfile_found=repo_cfg)
    cc = fake_make_config_context(backup_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config_context=cc)
    assert repo_cfg in result[0].snapshot_repofiles_to_copy


def test_repo_rulefile_included_in_snapshot_repofiles(tmp_path):
    repo_rules = tmp_path / ".rules"
    sc = fake_make_structural_context(tmp_path, repo_rulefile_found=repo_rules)
    cc = fake_make_config_context(backup_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config_context=cc)
    assert repo_rules in result[0].snapshot_repofiles_to_copy


def test_both_repo_files_included_in_order(tmp_path):
    repo_cfg = tmp_path / "mklists.yaml"
    repo_rules = tmp_path / ".rules"
    sc = fake_make_structural_context(
        tmp_path,
        repo_configfile_found=repo_cfg,
        repo_rulefile_found=repo_rules,
    )
    cc = fake_make_config_context(backup_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config_context=cc)
    assert result[0].snapshot_repofiles_to_copy == [repo_cfg, repo_rules]
