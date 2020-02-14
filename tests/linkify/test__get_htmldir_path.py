"""For a given data directory, constructs corresponding pathname in '_html/'."""

import os
import pytest
from pathlib import Path
from mklists.config import HTMLDIR_NAME
from mklists.linkify import _get_htmldir_path


def test_return_htmldir_pathname():
    """Returns pathname of HTML directory."""
    rd = "/Users/tbaker/tmp"
    hd = HTMLDIR_NAME
    dd = "/Users/tbaker/tmp/agenda"
    expected = Path("/Users/tbaker/tmp").joinpath(HTMLDIR_NAME, "agenda")
    assert _get_htmldir_path(datadir=dd, rootdir=rd, htmldir_name=hd) == expected


def test_return_htmldir_pathname_html_subdirectories_nested():
    """Structure of HTML directory mirrors structure of data directories."""
    rd = "/Users/tbaker/tmp"
    dd = "/Users/tbaker/tmp/a/b"
    expected = Path("/Users/tbaker/tmp").joinpath(HTMLDIR_NAME, "a/b")
    real = _get_htmldir_path(rootdir=rd, datadir=dd)
    assert real == expected


def test_exits_if_rootdir_cannot_be_found(tmp_path):
    """Raises exception if root directory cannot be found."""
    dd = Path(tmp_path).joinpath("agenda")
    dd.mkdir()
    os.chdir(dd)
    with pytest.raises(SystemExit):
        _get_htmldir_path(rootdir=None, datadir=dd)


def test_exit_if_htmldir_is_explicitly_given_as_none(tmp_path):
    """Raises exception if htmldir_name explicitly set to object of bad type."""
    rd = tmp_path
    dd = Path(tmp_path).joinpath("a")
    dd.mkdir()
    os.chdir(dd)
    with pytest.raises(SystemExit):
        _get_htmldir_path(rootdir=rd, htmldir_name=None)


def test_return_htmldir_pathname_datadir_name_not_supplied(tmp_path):
    """Returns pathname of HTML directory."""
    Path(tmp_path).joinpath("mklists.yml").write_text("config stuff")
    ab = Path(tmp_path).joinpath("a/b")
    ab.mkdir(parents=True, exist_ok=True)
    os.chdir(ab)
    assert HTMLDIR_NAME == "_html"
    expected = Path(tmp_path) / HTMLDIR_NAME / "a/b"
    assert _get_htmldir_path() == expected


def test_return_htmldir_path_specifying_different_html_name(tmp_path):
    """Returns pathname of HTML directory."""
    Path(tmp_path).joinpath("mklists.yml").write_text("config stuff")
    ab = Path(tmp_path).joinpath("a/b")
    ab.mkdir(parents=True, exist_ok=True)
    os.chdir(ab)
    different_htmldir_name = ".html"
    expected = Path(tmp_path) / different_htmldir_name / "a/b"
    assert _get_htmldir_path(htmldir_name=".html") == expected
