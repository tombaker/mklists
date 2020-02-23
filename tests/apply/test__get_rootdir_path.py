"""Returns root pathname of mklists repo wherever called in repo."""

import os
import pytest
from pathlib import Path
from mklists.apply import _find_rootdir_path
from mklists.config import CONFIGFILE_NAME, ROOTDIR_RULEFILE_NAME, DATADIR_RULEFILE_NAME

# pylint: disable=unused-argument
# These are just tests...


def test_find_rootdir_path_while_in_rootdir_using_tmp_path(tmp_path):
    """Returns root directory when called while already in root directory."""
    os.chdir(tmp_path)
    Path(CONFIGFILE_NAME).write_text("config stuff")
    assert Path(CONFIGFILE_NAME).exists()
    assert _find_rootdir_path() == tmp_path


def test_find_rootdir_path_while_in_rootdir(tmp_path):
    """Returns root directory when called in root directory."""
    os.chdir(tmp_path)
    Path(tmp_path).joinpath(CONFIGFILE_NAME).write_text("config stuff")
    Path(tmp_path).joinpath(ROOTDIR_RULEFILE_NAME).write_text("rule stuff")
    Path(tmp_path).joinpath("a/b/c").mkdir(parents=True, exist_ok=True)
    Path(tmp_path).joinpath("a", DATADIR_RULEFILE_NAME).write_text("rule stuff")
    assert Path(CONFIGFILE_NAME).exists()
    assert Path(ROOTDIR_RULEFILE_NAME).exists()
    assert _find_rootdir_path() == tmp_path == Path.cwd()


def test_find_rootdir_path_while_in_subdir_two_deep(tmp_path):
    """Returns root path even from non-data- and sub-sub-directories."""
    os.chdir(tmp_path)
    Path(tmp_path).joinpath(CONFIGFILE_NAME).write_text("config stuff")
    abc = Path(tmp_path) / "a/b/c"
    abc.mkdir(parents=True, exist_ok=True)
    os.chdir(abc)
    assert _find_rootdir_path() == tmp_path
    assert Path.cwd() == abc  # still in data directory


def test_raise_exception_when_configfile_not_found(tmp_path):
    """Raise ConfigFileNotFoundError if no config file found."""
    os.chdir(tmp_path)
    Path(tmp_path).joinpath(ROOTDIR_RULEFILE_NAME).write_text("rule stuff")
    a = Path(tmp_path) / "a"
    a.mkdir(parents=True, exist_ok=True)
    Path(a).joinpath(DATADIR_RULEFILE_NAME).write_text("rule stuff")
    os.chdir(a)
    with pytest.raises(SystemExit):
        _find_rootdir_path()


def test_find_rootdir_path_none_when_outside_repo(tmp_path):
    """Returns None as root directory when called outside repo."""
    os.chdir(tmp_path)
    os.chdir(os.pardir)
    with pytest.raises(SystemExit):
        _find_rootdir_path()
