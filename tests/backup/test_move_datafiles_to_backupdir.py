"""Moves datafiles to backup directory (just before writing new datafiles)."""

import os
from pathlib import Path
from mklists.backup import move_datafiles_to_backupdir
from mklists.config import BACKUPDIR_NAME, CONFIGFILE_NAME


def test_move_files_to_backupsub_no_datadir_specified(tmp_path):
    """Sets default of current directory if datadir directory is specified."""
    os.chdir(tmp_path)
    Path(CONFIGFILE_NAME).write_text("config stuff")  # for _get_rootdir_path()
    timestamp = "2020-02-13_1021_06488910"
    tmp_datadir = Path(tmp_path) / "data"
    tmp_datadir.mkdir()
    os.chdir(tmp_datadir)
    Path("a.txt").write_text("some content")
    Path("b.txt").write_text("some content")
    move_datafiles_to_backupdir(now=timestamp)  # for test, must specify timestamp
    expected_backup_path = Path(tmp_path) / BACKUPDIR_NAME / "data" / timestamp
    expected_backupdir_files = ["a.txt", "b.txt"]
    assert expected_backup_path.is_dir()
    assert Path(expected_backup_path).joinpath("a.txt").is_file()
    assert expected_backupdir_files == sorted(os.listdir(expected_backup_path))
    assert os.listdir(tmp_datadir) == []


def test_move_files_to_backupsub_with_datadir_specified(tmp_path):
    """Sets default of current directory if datadir directory is specified."""
    os.chdir(tmp_path)
    Path(CONFIGFILE_NAME).write_text("config stuff")  # for _get_rootdir_path()
    timestamp = "2020-02-13_1021_06488910"
    tmp_datadir = Path(tmp_path) / "data"
    tmp_datadir.mkdir()
    Path(tmp_datadir).joinpath("a.txt").write_text("some content")
    Path(tmp_datadir).joinpath("b.txt").write_text("some content")
    move_datafiles_to_backupdir(datadir=tmp_datadir, now=timestamp)
    expected_backup_path = Path(tmp_path) / BACKUPDIR_NAME / "data" / timestamp
    expected_backupdir_files = ["a.txt", "b.txt"]
    assert expected_backup_path.is_dir()
    assert Path(expected_backup_path).joinpath("a.txt").is_file()
    assert expected_backupdir_files == sorted(os.listdir(expected_backup_path))
    assert os.listdir(tmp_datadir) == []
    assert Path.cwd() == tmp_path
