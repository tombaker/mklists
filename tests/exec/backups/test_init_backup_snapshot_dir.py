"""Tests $MKLMKL/exec/backups.py"""

from mklists.exec.backups import init_snapshot_dir


def test_create_directory_outside_datatree(tmp_path):
    """Backup directories may be created outside the mklists datatree.

    Note: init_snapshot_dir does not care whether "mklists.yaml" or
    "mklists.rules" are valid names for the mklists config settings and global rules.
    It simply copies the pathnames it is passed, if they exist, to the backup
    directory. The file "mklists.rules" is therefore deliberately misspelled here
    to make this point.
    """
    config_rootdir = tmp_path / "datatree"
    config_rootdir.mkdir()

    datatree_configfile = config_rootdir / "mklists.yaml"
    datatree_configfile.write_text("config")

    datatree_rulefile = config_rootdir / "mlksits.ruels"  # deliberately misspelled
    datatree_rulefile.write_text("rules")

    snapshot_dir = tmp_path / "backups" / "2026-02-01_162616893737_pass01"
    snapshot_datatree_configfiles = [datatree_configfile, datatree_rulefile]

    init_snapshot_dir(
        snapshot_dir=snapshot_dir,
        snapshot_datatree_configfiles=snapshot_datatree_configfiles,
    )

    assert snapshot_dir.is_dir()
    assert (snapshot_dir / datatree_configfile.name).read_text() == "config"
    assert (snapshot_dir / datatree_rulefile.name).read_text() == "rules"


def test_create_directory_even_if_no_config_files_found(tmp_path):
    """If mklists.yaml and mklists.rules not found, create backup directory anyway."""
    config_rootdir = tmp_path / "datatree"
    config_rootdir.mkdir()

    snapshot_dir = config_rootdir / "backups" / "2026-02-01_162616893737_pass01"
    snapshot_datatree_configfiles = []

    init_snapshot_dir(
        snapshot_dir=snapshot_dir,
        snapshot_datatree_configfiles=snapshot_datatree_configfiles,
    )

    assert snapshot_dir.is_dir()
