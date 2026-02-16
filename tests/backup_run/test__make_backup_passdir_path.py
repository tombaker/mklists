"""Tests ~/github/tombaker/mklists/src/mklists/backup_run.py """


import pytest
# from mklists.backup_run import _make_passdir_path


@pytest.mark.skip
def test_make_backuproot_path_absolute(tmp_path):
    """Create backup root directory path as absolute pathname."""
    backups_rootdir = tmp_path / "backups"

    path = _make_passdir_path(
        backups_rootdir=backups_rootdir,
        timestamp="2026-02-01_162616",
        pass_number=2,
    )

    assert path == backups_rootdir / "2026-02-01_162616_pass02"
