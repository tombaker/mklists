"""Tests for $MKLMKL/exec/safety.py"""

import re
import pytest
from mklists.config import SafetyConfig
from mklists.exec.safety import _check_is_valid_name


@pytest.fixture
def safety_config():
    return SafetyConfig(
        invalid_filename_patterns=[
            re.compile(r"\.swp$"),
            re.compile(r"\.tmp$"),
            re.compile(r"~$"),
        ],
    )


def test_valid_filename_passes(safety_config):
    """Valid filename passes."""
    _check_is_valid_name("data.txt", safety_config)


def test_invalid_characters_fail(safety_config):
    """If filename has invalid characters, raise ValueError."""
    _check_is_valid_name("bad filenäme.txt", safety_config)


def test_forbidden_suffix_fails(safety_config):
    """If filename has invalid suffix, raise ValueError."""
    with pytest.raises(ValueError) as exc:
        _check_is_valid_name("notes.swp", safety_config)

    err = exc.value.args[0]
    assert err["reason"] == "matches forbidden filename pattern"
    assert err["pattern"] == r"\.swp$"


def test_forbidden_pattern_checked_after_valid_chars(safety_config):
    """Valid characters checked first, then suffix (or other regexes)."""
    with pytest.raises(ValueError) as exc:
        _check_is_valid_name("goodname.tmp", safety_config)

    err = exc.value.args[0]
    assert err["reason"] == "matches forbidden filename pattern"
