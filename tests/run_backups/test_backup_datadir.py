"""Tests $MKLMKL/run_backups.py """

import pytest
from mklists.run_backups import backup_datadirs


def test_write_backup_copies_all_datadirs(tmp_path):
    """Create files to back up, back them up, read backup files to confirm."""
    pass_backup_root = tmp_path / "backups" / "2026-02-01_162616893737_pass01"

    datadir_a = tmp_path / "repo" / "a"
    datadir_b = tmp_path / "repo" / "b"
    datadir_a.mkdir(parents=True)
    datadir_b.mkdir(parents=True)

    (datadir_a / "a.txt").write_text("A")
    (datadir_b / "b.txt").write_text("B")

    backup_datadirs(
        datadirs=[datadir_a, datadir_b],
        pass_backup_root=pass_backup_root,
    )

    assert (pass_backup_root / "a" / "a.txt").read_text() == "A"
    assert (pass_backup_root / "b" / "b.txt").read_text() == "B"



def test_write_backup_raises_if_pass_root_exists(tmp_path):
    pass_backup_root = tmp_path / "backups" / "pass01"
    pass_backup_root.mkdir(parents=True)

    datadir = tmp_path / "repo" / "a"
    datadir.mkdir(parents=True)

    with pytest.raises(FileExistsError):
        backup_datadirs(
            datadirs=[datadir],
            pass_backup_root=pass_backup_root,
        )
