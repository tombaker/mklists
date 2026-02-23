"""Tests $MKLRUN/backups.py"""

from mklists.run.backups import init_backup_snapshot_dir


def test_create_directory_outside_repo(tmp_path):
    """Backup directories may be created outside mklists repo.

    Note: init_backup_snapshot_dir does not care whether "mklists.yaml" or
    "mklists.rules" are valid names for the mklists config settings and global rules.
    It simply copies the pathnames it is passed, if they exist, to the backup
    directory. The file "mklists.rules" is therefore deliberately misspelled here
    to make this point.
    """
    config_rootdir = tmp_path / "repo"
    config_rootdir.mkdir()

    repo_configfile = config_rootdir / "mklists.yaml"
    repo_configfile.write_text("config")

    repo_rulefile = config_rootdir / "mlksits.ruels"  # deliberately misspelled
    repo_rulefile.write_text("rules")

    backup_snapshot_dir = tmp_path / "backups" / "2026-02-01_162616893737_pass01"

    init_backup_snapshot_dir(
        backup_snapshot_dir=backup_snapshot_dir,
        repo_configfile=repo_configfile,
        repo_rulefile=repo_rulefile,
    )

    assert backup_snapshot_dir.is_dir()
    assert (backup_snapshot_dir / repo_configfile.name).read_text() == "config"
    assert (backup_snapshot_dir / repo_rulefile.name).read_text() == "rules"


def test_create_directory_even_if_no_config_files_found(tmp_path):
    """If mklists.yaml and mklists.rules not found, create backup directory anyway."""
    config_rootdir = tmp_path / "repo"
    config_rootdir.mkdir()

    backup_snapshot_dir = config_rootdir / "backups" / "2026-02-01_162616893737_pass01"

    init_backup_snapshot_dir(
        backup_snapshot_dir=backup_snapshot_dir,
        repo_configfile=None,
        repo_rulefile=None,
    )

    assert backup_snapshot_dir.is_dir()
