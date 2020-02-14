"""Coerce 'target' filename (string or Pathlike object) to valid string."""

import pytest
from pathlib import Path
from mklists.rules import Rule


def test_target_is_valid_filename():
    """Field 4 (target) must be a valid filename."""
    rule_obj = Rule(1, "NOW", "a", "b", 2)
    rule_obj._coerce_target_as_valid_filename()
    assert rule_obj.target == "b"


def test_pathlike_object_is_valid_filename():
    """Source could be a Path object."""
    rule_obj = Rule(1, "NOW", "a", Path("b"), 2)
    rule_obj._coerce_target_as_valid_filename()
    assert rule_obj.target == "b"


def test_raise_exception_given_bad_filename_string():
    """Field 4 (target) must not contain invalid characters."""
    rule_obj = Rule(1, "NOW", "a", "b/2:", 2)
    with pytest.raises(SystemExit):
        rule_obj._coerce_target_as_valid_filename()


def test_raise_exception_given_target_filename_none():
    """Field 4 (target) must not be None."""
    rule_obj = Rule(1, "NOW", "a", None, 2)
    with pytest.raises(SystemExit):
        rule_obj._coerce_target_as_valid_filename()
