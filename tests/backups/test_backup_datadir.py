"""@@@"""

import pytest
from mklists.backup_datadir import backup_datadir


@pytest.mark.skip
def test_backup_datadir_creates_backup(tmp_path):
    """Happy path."""
    passdir = tmp_path / "backups" / "2026-02-01_162616893737_pass01"
    passdir.mkdir(parents=True, exist_ok=True)

    datadir = tmp_path / "repo" / "a"
    datadir.mkdir(parents=True, exist_ok=True)
    (datadir / "file1.txt").write_text("hello")

    passdir = backup_datadir(
        datadir=datadir,
        passdir=passdir,
        backup_depth=2,
    )

    # backup root created
    assert passdir.is_dir()
    assert passdir.name == "2026-02-01_162616893737_pass01"

    # datadir copied
    assert (passdir / "a").is_dir()
    assert (passdir / "a" / "file1.txt").read_text() == "hello"


@pytest.mark.skip
def test_backup_datadir_raises_if_target_backupdir_exists(tmp_path):
    """Raise FileExistsError if backup subdirectory for datadir already exists."""
    config_rootdir = tmp_path / "repo"
    config_rootdir.mkdir()

    datadir = config_rootdir / "data"
    datadir.mkdir()
    (datadir / "a.txt").write_text("hello\n")

    passdir = tmp_path / "backups" / "2026-02-01_162616893737_pass01"
    passdir.mkdir(parents=True)

    existing_data_backupdir = passdir / datadir.name
    existing_data_backupdir.mkdir()  # <-- critical setup

    # Act + Assert
    with pytest.raises(FileExistsError):
        backup_datadir(
            datadir=datadir,
            passdir=passdir,
            backup_depth=2,
        )
