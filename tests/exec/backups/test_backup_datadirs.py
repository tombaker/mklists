"""Tests $MKLMKL/exec/backups.py"""

import pytest
from mklists.exec.backups import backup_datadirs, init_backup_snapshot_dir


def test_write_backup_copies_all_datadirs(tmp_path):
    """Create files to back up, back them up, read backup files to confirm."""
    backup_snapshot_dir = tmp_path / "backups" / "2026-02-01_162616893737_pass01"
    backup_snapshot_dir.mkdir(parents=True)

    datadir_a = tmp_path / "repo" / "a"
    datadir_b = tmp_path / "repo" / "b"
    datadir_a.mkdir(parents=True)
    datadir_b.mkdir(parents=True)

    (datadir_a / "a.txt").write_text("A")
    (datadir_b / "b.txt").write_text("B")

    backup_datadirs(
        datadirs=[datadir_a, datadir_b],
        backup_snapshot_dir=backup_snapshot_dir,
    )

    assert (backup_snapshot_dir / "a" / "a.txt").read_text() == "A"
    assert (backup_snapshot_dir / "b" / "b.txt").read_text() == "B"


def test_write_backup_raises_if_backupdir_not_exist(tmp_path):
    """Raise FileNotFoundError if backup snapshot directory does not already exist."""
    backup_snapshot_dir = tmp_path / "backups" / "pass01"

    datadir = tmp_path / "repo" / "a"
    datadir.mkdir(parents=True)

    with pytest.raises(FileNotFoundError):
        backup_datadirs(
            datadirs=[datadir],
            backup_snapshot_dir=backup_snapshot_dir,
        )


def test_integration_with_init_backup_snapshot_dir(tmp_path):
    """Integration of init_backup_snapshot_dir and backup_datadirs."""
    backup_snapshot_dir = tmp_path / "backups" / "pass01"

    repo_configfile = tmp_path / "mklists.yaml"
    repo_configfile.write_text("config\n")

    repo_rulefile = tmp_path / "mklists.rules"
    repo_rulefile.write_text("rules\n")

    init_backup_snapshot_dir(
        backup_snapshot_dir=backup_snapshot_dir,
        repo_configfile=repo_configfile,
        repo_rulefile=repo_rulefile,
    )

    assert (backup_snapshot_dir / "mklists.yaml").read_text() == "config\n"
    assert (backup_snapshot_dir / "mklists.rules").read_text() == "rules\n"

    datadir_a = tmp_path / "repo" / "a"
    datadir_b = tmp_path / "repo" / "b"
    datadir_a.mkdir(parents=True)
    datadir_b.mkdir(parents=True)

    (datadir_a / "a.txt").write_text("A")
    (datadir_b / "b.txt").write_text("B")

    backup_datadirs(
        datadirs=[datadir_a, datadir_b],
        backup_snapshot_dir=backup_snapshot_dir,
    )

    assert (backup_snapshot_dir / "a" / "a.txt").read_text() == "A"
    assert (backup_snapshot_dir / "b" / "b.txt").read_text() == "B"
