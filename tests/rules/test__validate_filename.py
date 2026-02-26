"""Returns passed-in filename after validation and type coercion."""

import pytest
from mklists.errors import FilenameError
from mklists.rules.load import _validate_filename


def test_valid_filename():
    """Happy path."""
    _validate_filename("foobar.txt")


def test_filename_must_not_be_empty_string():
    """@@@"""
    with pytest.raises(FilenameError):
        _validate_filename("")


def test_filename_must_have_at_least_one_alphanumeric_character():
    """Filename must have at least one alphanumeric character."""
    with pytest.raises(FilenameError):
        _validate_filename(":.:.,.")


def test_filename_must_not_have_forward_slash():
    """Filename must not have forward slash (as used in pathnames)."""
    with pytest.raises(FilenameError):
        _validate_filename("foo/bar.txt")


def test_filename_may_have_space():
    """Filename may have spaces (at user's risk)."""
    _validate_filename("My File.txt")


def test_filename_may_have_umlautted_character():
    """Filename may have an umlaut."""
    _validate_filename("föö.txt")


def test_filename_must_be_string():
    """Filename must be string (though in context of rules, it always will be)."""
    with pytest.raises(FilenameError):
        _validate_filename(filename=None)


def test_filename_must_not_start_with_dot():
    """Filename must not start with dot (for "hidden" file)."""
    with pytest.raises(FilenameError):
        _validate_filename(".foobar.txt")
