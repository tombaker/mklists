"""Tests $MKLMKL/plan/resolve.py: _resolve_pass_plans."""

from pathlib import Path
from mklists.config.model import (
    BackupConfig,
    LinkifyConfig,
    RoutingConfig,
    SafetyConfig,
    Config,
)
from mklists.structure.model import (
    DatadirStructuralContext,
    StartdirStructuralContext,
    StructuralContext,
)
from mklists.plan.model import PassPlan
from mklists.plan.resolve import _resolve_pass_plans


def fake_make_config(
    *,
    backup_enabled: bool,
    routing_enabled: bool = False,
) -> Config:
    """Fake stand-in makes Config object by varying key variables.

    backup_enabled=True  → backup_rootdir=Path("backups") (non-None enables backup)
    backup_enabled=False → backup_rootdir=None (None disables backup)
    routing_enabled=True → non-empty routing_dict (non-empty dict enables routing)
    routing_enabled=False → empty routing_dict
    """
    return Config(
        verbose=False,
        configfile_used=Path("foo"),
        config_rootdir=Path("bar"),
        backup=BackupConfig(
            backup_rootdir=Path("backups") if backup_enabled else None,
            backup_depth=2,
        ),
        routing=RoutingConfig(
            routing_dict={"placeholder.txt": Path("/some/dir")} if routing_enabled else {},
        ),
        safety=SafetyConfig(
            invalid_filename_patterns=[],
        ),
        linkify=LinkifyConfig(
            linkify_md_dir=None,
            linkify_html_dir=None,
        ),
    )


def fake_make_structural_context(
    tmp_path: Path,
    *,
    num_datadirs: int = 1,
    datatree_configfile_found: Path | None = None,
    datatree_rulefile_found: Path | None = None,
) -> StructuralContext:
    """Creates a StructuralContext with a valid config_rootdir.

    Note:
        Defaults to datatree_configfile_found=tmp_path/"mklists.yaml" so that
        is_datatree_root=True and config_rootdir=tmp_path (the startdir).
        Bypasses need for some testing boilerplate.

        Pass explicit datatree_configfile_found=None only when datatree_rulefile_found
        is set (still gives is_datatree_root=True).
    """
    if datatree_configfile_found is None and datatree_rulefile_found is None:
        datatree_configfile_found = tmp_path / "mklists.yaml"

    return StructuralContext(
        startdir_context=StartdirStructuralContext(
            startdir=tmp_path,
            datatree_configfile_found=datatree_configfile_found,
            datatree_rulefile_found=datatree_rulefile_found,
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
    """Backups disabled: one pass."""
    sc = fake_make_structural_context(tmp_path)
    cc = fake_make_config(backup_enabled=False)
    result = _resolve_pass_plans(structural_context=sc, config=cc)
    assert result == [PassPlan(snapshot_dir=None, snapshot_datatree_configfiles=[])]
    assert len(result) == 1


def test_backup_disabled_routing_enabled_single_datadir_returns_one_pass(tmp_path):
    """Backups disabled, Routing enabled, one datadir: one pass, snapshot_dir=None."""
    sc = fake_make_structural_context(tmp_path, num_datadirs=1)
    cc = fake_make_config(backup_enabled=False, routing_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config=cc)
    assert result == [PassPlan(snapshot_dir=None, snapshot_datatree_configfiles=[])]


def test_backup_disabled_routing_enabled_multiple_datadirs_returns_two_passes(tmp_path):
    """Routing enabled, multiple datadirs: two passes, both snapshot_dir=None."""
    sc = fake_make_structural_context(tmp_path, num_datadirs=2)
    cc = fake_make_config(backup_enabled=False, routing_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config=cc)
    assert len(result) == 2
    assert all(p.snapshot_dir is None for p in result)
    assert all(p.snapshot_datatree_configfiles == [] for p in result)


# ----- pass count ------------------------------------------------------------


def test_backup_enabled_routing_disabled_returns_one_pass(tmp_path):
    """Backups enabled, one datadir: one pass."""
    sc = fake_make_structural_context(tmp_path)
    cc = fake_make_config(backup_enabled=True, routing_enabled=False)
    result = _resolve_pass_plans(structural_context=sc, config=cc)
    assert len(result) == 1


def test_routing_enabled_single_datadir_returns_one_pass(tmp_path):
    """Backups and routing enabled, one datadir: still one pass."""
    sc = fake_make_structural_context(tmp_path, num_datadirs=1)
    cc = fake_make_config(backup_enabled=True, routing_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config=cc)
    assert len(result) == 1


def test_routing_enabled_multiple_datadirs_returns_two_passes(tmp_path):
    """Backups and routing enabled, multiple datadirs: two passes."""
    sc = fake_make_structural_context(tmp_path, num_datadirs=2)
    cc = fake_make_config(backup_enabled=True, routing_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config=cc)
    assert len(result) == 2


# ----- snapshot_dir paths ----------------------------------------------------


def test_snapshot_dir_is_under_config_rootdir_and_backup_rootdir(tmp_path):
    """Backups enabled: config_rootdir (tmp_path) / 'backups' / snapshot_dir."""
    sc = fake_make_structural_context(tmp_path)
    cc = fake_make_config(backup_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config=cc)
    assert result[0].snapshot_dir.parent == tmp_path / "backups"


def test_single_pass_snapshot_dir_name_ends_with_01(tmp_path):
    """Backups enabled: single-pass snapshot_dir name ends with '_01'."""
    sc = fake_make_structural_context(tmp_path)
    cc = fake_make_config(backup_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config=cc)
    assert result[0].snapshot_dir.name.endswith("_01")


def test_two_passes_have_01_and_02_suffixes(tmp_path):
    """Backups enabled: multi-pass snapshot_dir names end with '_01', '_02'."""
    sc = fake_make_structural_context(tmp_path, num_datadirs=2)
    cc = fake_make_config(backup_enabled=True, routing_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config=cc)
    assert result[0].snapshot_dir.name.endswith("_01")
    assert result[1].snapshot_dir.name.endswith("_02")


def test_two_passes_share_same_timestamp(tmp_path):
    """Both snapshot dirs differ only in '_01'/'_02' suffix, proving one timestamp."""
    sc = fake_make_structural_context(tmp_path, num_datadirs=2)
    cc = fake_make_config(backup_enabled=True, routing_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config=cc)
    name0 = result[0].snapshot_dir.name
    name1 = result[1].snapshot_dir.name
    assert name0[:-3] == name1[:-3]


# ----- snapshot_datatree_configfiles --------------------------------------------


def test_datatree_configfile_included_in_snapshot_datatree_configfiles(tmp_path):
    """If only 'mklists.yaml', then only one datatree config file to snapshot is listed."""
    datatree_cfg = tmp_path / "mklists.yaml"
    sc = fake_make_structural_context(tmp_path, datatree_configfile_found=datatree_cfg)
    cc = fake_make_config(backup_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config=cc)
    assert datatree_cfg in result[0].snapshot_datatree_configfiles
    assert len(result[0].snapshot_datatree_configfiles) == 1


def test_datatree_rulefile_included_in_snapshot_datatree_configfiles(tmp_path):
    """If only '.rules', then only one datatree config file to snapshot is listed."""
    datatree_rules = tmp_path / ".rules"
    sc = fake_make_structural_context(tmp_path, datatree_rulefile_found=datatree_rules)
    cc = fake_make_config(backup_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config=cc)
    assert datatree_rules in result[0].snapshot_datatree_configfiles
    assert len(result[0].snapshot_datatree_configfiles) == 1


def test_both_datatree_configfiles_included_in_order(tmp_path):
    """If both '.rules' and 'mklists.yaml', then two datatree config files to snapshot listed."""
    datatree_cfg = tmp_path / "mklists.yaml"
    datatree_rules = tmp_path / ".rules"
    sc = fake_make_structural_context(
        tmp_path,
        datatree_configfile_found=datatree_cfg,
        datatree_rulefile_found=datatree_rules,
    )
    cc = fake_make_config(backup_enabled=True)
    result = _resolve_pass_plans(structural_context=sc, config=cc)
    assert result[0].snapshot_datatree_configfiles == [datatree_cfg, datatree_rules]
    assert len(result[0].snapshot_datatree_configfiles) == 2
