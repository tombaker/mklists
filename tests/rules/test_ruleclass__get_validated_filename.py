"""Returns passed-in filename after validation and type coercion."""

import os
import pytest
from pathlib import Path
from mklists.rules import _get_validated_filename


def test_returns_validated_filename():
    """Passes when filename is valid."""
    assert _get_validated_filename("foobar.txt")


def test_returns_validated_filename_even_for_pathlike_object():
    """Passes when Pathlike object filename is valid."""
    assert _get_validated_filename(Path("foobar.txt"))


def test_exits_if_illegal_character_used():
    """Exits if illegal character found in filename."""
    with pytest.raises(SystemExit):
        _get_validated_filename("foo;bar.txt")


def test_exits_if_no_alphanumeric_characters_used():
    """Exits if no alphanumeric characters found in filename."""
    with pytest.raises(SystemExit):
        _get_validated_filename("..:.,.")


def test_exits_if_filename_contains_forward_slash():
    """Exits if forward slash (for pathname components) found in filename."""
    with pytest.raises(SystemExit):
        _get_validated_filename("foo/bar.txt")


def test_exits_if_filename_contains_space():
    """Exits if space found in filename."""
    with pytest.raises(SystemExit):
        _get_validated_filename("My File.txt")


def test_exits_if_filename_contains_umlaut():
    """Exits if umlaut found in filename."""
    with pytest.raises(SystemExit):
        _get_validated_filename("föö.txt")


def test_exits_if_filename_is_none(tmp_path):
    """Exits if filename is None."""
    with pytest.raises(SystemExit):
        _get_validated_filename(filename=None)


def test_exits_if_filename_is_empty(tmp_path):
    """Exits if given filename is empty string."""
    with pytest.raises(SystemExit):
        _get_validated_filename(filename="")


def test_exits_if_filename_already_exists_as_directory(tmp_path):
    """Exits if given filename already exists as directory name."""
    os.chdir(tmp_path)
    name_to_be_tested = "foobar"
    foobar = Path(name_to_be_tested)
    foobar.mkdir()
    with pytest.raises(SystemExit):
        _get_validated_filename(name_to_be_tested)


def test_exits_if_filename_starts_with_dot():
    """Exits if filename is "hidden" (starts with a dot)."""
    fname = ".foobar.txt"
    with pytest.raises(SystemExit):
        _get_validated_filename(fname)


def test_exits_if_filename_matches_bad_pattern():
    """Exits if filename matches regex for an Emacs backup file."""
    fname = "foobar.txt~"
    with pytest.raises(SystemExit):
        _get_validated_filename(fname)
