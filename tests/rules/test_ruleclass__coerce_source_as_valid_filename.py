"""Coerce 'source' filename (string or Pathlike object) to valid string."""


import pytest
from pathlib import Path
from mklists.rules import Rule


def test_source_is_valid_filename():
    """Field 3 (source) must be a valid filename."""
    rule_obj = Rule(1, "NOW", "a", "b", 2)
    rule_obj._coerce_source_as_valid_filename()
    assert rule_obj.source == "a"


def test_pathlike_object_is_valid_filename():
    """Source could be a Path object."""
    rule_obj = Rule(1, "NOW", Path("a"), "b", 2)
    rule_obj._coerce_source_as_valid_filename()
    assert rule_obj.source == "a"


def test_raise_exception_given_bad_filename_string():
    """Field 3 (source) must not contain invalid characters."""
    rule_obj = Rule(1, "NOW", "a/2:", "b", 2)
    with pytest.raises(SystemExit):
        rule_obj._coerce_source_as_valid_filename()


def test_raise_exception_given_source_filename_none():
    """Field 3 (source) must not be None."""
    rule_obj = Rule(1, "NOW", None, "b", 2)
    with pytest.raises(SystemExit):
        rule_obj._coerce_source_as_valid_filename()
