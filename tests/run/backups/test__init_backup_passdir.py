"""Tests $MKLRUN/backups.py"""

import pytest
from mklists.run.backups import _init_passdir


@pytest.mark.skip
def test_create_directory_outside_repo(tmp_path):
    """Backup directories may be created outside mklists repo.

    Note: _init_passdir does not care whether "mklists.yaml" or "mklists.rules"
    are valid names for the mklists config settings and global rules. It simply
    copies the pathnames it is passed, if they exist, to the backup directory.
    The file "mklists.rules" is therefore deliberately misspelled here to make
    this point.
    """
    config_rootdir = tmp_path / "repo"
    config_rootdir.mkdir()

    user_configfile = config_rootdir / "mklists.yaml"
    user_configfile.write_text("config")

    global_rulefile = config_rootdir / "mlksits.ruels"  # deliberately misspelled
    global_rulefile.write_text("rules")

    passdir = tmp_path / "backups" / "2026-02-01_162616893737_pass01"

    _init_passdir(
        passdir=passdir,
        user_configfile=user_configfile,
        global_rulefile=global_rulefile,
    )

    assert passdir.is_dir()
    assert (passdir / user_configfile.name).read_text() == "config"
    assert (passdir / global_rulefile.name).read_text() == "rules"


@pytest.mark.skip
def test_create_directory_even_if_no_config_files_found(tmp_path):
    """If mklists.yaml and mklists.rules not found, create backup directory anyway."""
    config_rootdir = tmp_path / "repo"
    config_rootdir.mkdir()

    passdir = config_rootdir / "backups" / "2026-02-01_162616893737_pass01"

    _init_passdir(
        passdir=passdir,
        user_configfile=None,
        global_rulefile=None,
    )

    assert passdir.is_dir()
    # assert len(passdir.iterdir()) == 0
