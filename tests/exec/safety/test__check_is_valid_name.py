"""Tests for $MKLMKL/exec/safety.py"""

import re
from pathlib import Path
import pytest
from mklists.config.model import SafetyConfig
from mklists.errors import SafetyError
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
    _check_is_valid_name(Path("/datadir/data.txt"), safety_config)


def test_invalid_characters_fail(safety_config):
    """If filename has invalid characters, raise SafetyError."""
    _check_is_valid_name(Path("/datadir/bad filenäme.txt"), safety_config)


def test_forbidden_suffix_fails(safety_config):
    """If filename has invalid suffix, raise SafetyError."""
    with pytest.raises(SafetyError) as exc:
        _check_is_valid_name(Path("/datadir/notes.swp"), safety_config)

    assert "matches forbidden filename pattern" in str(exc.value)
    assert r"\.swp$" in str(exc.value)
    assert "Processing interrupted." in str(exc.value)


def test_forbidden_pattern_checked_after_valid_chars(safety_config):
    """Valid characters checked first, then suffix (or other regexes)."""
    with pytest.raises(SafetyError) as exc:
        _check_is_valid_name(Path("/datadir/goodname.tmp"), safety_config)

    assert "matches forbidden filename pattern" in str(exc.value)
    assert "Processing interrupted." in str(exc.value)
