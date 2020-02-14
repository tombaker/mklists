"""Returns passed-in filename after validation and type coercion."""

import os
from pathlib import Path
import pytest
from mklists.rules import _get_validated_filename


def test_returns_validated_filename():
    """Passes when filename is valid."""
    assert _get_validated_filename("foobar.txt")


def test_returns_validated_filename_even_for_pathlike_object():
    """Passes when Pathlike object filename is valid."""
    assert _get_validated_filename(Path("foobar.txt"))


def test_exit_if_illegal_character_used():
    """Returns False when illegal character found in filename."""
    with pytest.raises(SystemExit):
        _get_validated_filename("foo;bar.txt")


def test_exit_if_filename_contains_forward_slash():
    """Returns False when forward slash found in filename."""
    with pytest.raises(SystemExit):
        _get_validated_filename("foo/bar.txt")


def test_exit_if_filename_contains_umlaut():
    """Returns False when umlaut found in filename."""
    with pytest.raises(SystemExit):
        _get_validated_filename("föö.txt")


def test_exit_if_filename_is_none(tmp_path):
    """Raises exception when given filename is None."""
    with pytest.raises(SystemExit):
        _get_validated_filename(filename=None)


def test_exit_if_filename_is_empty(tmp_path):
    """Raises exception when given filename is empty string."""
    with pytest.raises(SystemExit):
        _get_validated_filename(filename="")


def test_exit_if_filename_already_exists_as_directory(tmp_path):
    """Raises exception when given filename already exists as directory name."""
    os.chdir(tmp_path)
    name_to_be_tested = "foobar"
    foobar = Path(name_to_be_tested)
    foobar.mkdir()
    with pytest.raises(SystemExit):
        _get_validated_filename(name_to_be_tested)


def test_exit_if_filename_starts_with_dot():
    """Returns False for filename of hidden dotfile."""
    fname = ".foobar.txt"
    with pytest.raises(SystemExit):
        _get_validated_filename(fname)


def test_exit_if_filename_matches_bad_pattern():
    """Returns False for filename of an Emacs backup file."""
    fname = "foobar.txt~"
    with pytest.raises(SystemExit):
        _get_validated_filename(fname)
