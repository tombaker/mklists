"""Tests $MKLMKL/exec/backups.py"""

from mklists.exec.backups import init_snapshot_dir


def test_create_directory_outside_repo(tmp_path):
    """Backup directories may be created outside mklists repo.

    Note: init_snapshot_dir does not care whether "mklists.yaml" or
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

    snapshot_dir = tmp_path / "backups" / "2026-02-01_162616893737_pass01"
    snapshot_repofiles_to_copy = [repo_configfile, repo_rulefile]

    init_snapshot_dir(
        snapshot_dir=snapshot_dir,
        snapshot_repofiles_to_copy=snapshot_repofiles_to_copy,
    )

    assert snapshot_dir.is_dir()
    assert (snapshot_dir / repo_configfile.name).read_text() == "config"
    assert (snapshot_dir / repo_rulefile.name).read_text() == "rules"


def test_create_directory_even_if_no_config_files_found(tmp_path):
    """If mklists.yaml and mklists.rules not found, create backup directory anyway."""
    config_rootdir = tmp_path / "repo"
    config_rootdir.mkdir()

    snapshot_dir = config_rootdir / "backups" / "2026-02-01_162616893737_pass01"
    snapshot_repofiles_to_copy = []

    init_snapshot_dir(
        snapshot_dir=snapshot_dir,
        snapshot_repofiles_to_copy=snapshot_repofiles_to_copy,
    )

    assert snapshot_dir.is_dir()
