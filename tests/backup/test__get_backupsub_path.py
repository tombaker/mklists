"""Returns full pathname of backup directory."""

import os
import pytest
from pathlib import Path
from mklists.config import CONFIGFILE_NAME
from mklists.backup import _form_backupsub_pathname


def test_form_backupsub_pathname(tmp_path):
    """Returns backups Path named for current data directory."""
    os.chdir(tmp_path)
    Path(CONFIGFILE_NAME).write_text("config stuff")
    backdir = "_backups"
    datestr = "2020-01-03_1646"
    cwd = Path("agenda").resolve()
    cwd.mkdir()
    os.chdir(cwd)
    actual = _form_backupsub_pathname(backupdir_name=backdir, now=datestr)
    expected = Path(tmp_path) / backdir / cwd.name / datestr
    expected_explicit = Path(tmp_path) / "_backups" / "agenda" / "2020-01-03_1646"
    assert Path(cwd).resolve() == Path.cwd()  # directory did not change
    assert actual == expected
    assert actual == expected_explicit


def test_form_backupsub_pathname_given_datadir(tmp_path):
    """Returns backups Path named for specified working directory."""
    os.chdir(tmp_path)
    Path(CONFIGFILE_NAME).write_text("config stuff")
    cwd = Path(tmp_path).joinpath("todolists/a")
    cwd.mkdir(parents=True, exist_ok=True)
    shortname_expected = "todolists_a"
    backdir = "_backups"
    datestr = "2020-01-03_1646_06488910"
    actual = _form_backupsub_pathname(datadir=cwd, backupdir_name=backdir, now=datestr)
    expected = Path(tmp_path) / backdir / shortname_expected / datestr
    assert actual == expected


def test_form_backupsub_pathname_given_datadir_with_slash(tmp_path):
    """Returns backups Path named for specified working directory ending with slash."""
    os.chdir(tmp_path)
    Path(CONFIGFILE_NAME).write_text("config stuff")
    cwd = Path(tmp_path).joinpath("todolists/a/")
    cwd.mkdir(parents=True, exist_ok=True)
    shortname_expected = "todolists_a"
    backdir = "_backups"
    datestr = "2020-01-03_1646_06488910"
    actual = _form_backupsub_pathname(datadir=cwd, backupdir_name=backdir, now=datestr)
    expected = Path(tmp_path) / backdir / shortname_expected / datestr
    assert actual == expected


def test_raise_exception_if_rootdir_not_found(tmp_path):
    """Raises exception if no rootdir is found (rootdir is None)."""
    os.chdir(tmp_path)
    with pytest.raises(SystemExit):
        _form_backupsub_pathname()


def test_exit_if_passed_datadir_argument_of_wrong_type(tmp_path):
    """Raises exception if an argument of the wrong type is passed."""
    os.chdir(tmp_path)
    with pytest.raises(SystemExit):
        _form_backupsub_pathname(["asdf"])


def test_exit_if_passed_backupdir_name_argument_of_wrong_type(tmp_path):
    """Raises exception if an argument of the wrong type is passed."""
    os.chdir(tmp_path)
    with pytest.raises(SystemExit):
        _form_backupsub_pathname(backupdir_name=123456)
