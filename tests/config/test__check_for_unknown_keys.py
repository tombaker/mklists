"""Tests for _check_for_unknown_keys in mklists/config/resolve.py"""

from pathlib import Path
import pytest
from mklists.config.resolve import _check_for_unknown_keys
from mklists.errors import ConfigError

CONFIGFILE = Path("mklists.yaml")


def test_valid_top_level_key_passes():
    """A known top-level key raises no error."""
    _check_for_unknown_keys({"verbose": True}, {"verbose": True}, CONFIGFILE)


def test_unknown_top_level_key_raises():
    """An unknown top-level key raises ConfigError naming the config file."""
    with pytest.raises(ConfigError, match="mklists.yaml.*'linkify_dir'"):
        _check_for_unknown_keys({"linkify_dir": ".linkify"}, {"linkify": {}}, CONFIGFILE)


def test_valid_nested_key_passes():
    """A known nested key raises no error."""
    _check_for_unknown_keys(
        {"linkify": {"linkify_md_dir": None}},
        {"linkify": {"linkify_md_dir": None, "linkify_html_dir": None}},
        CONFIGFILE,
    )


def test_unknown_nested_key_raises():
    """An unknown nested key raises ConfigError with filename and dot-separated path."""
    with pytest.raises(ConfigError, match="mklists.yaml.*'linkify.linkify_dir'"):
        _check_for_unknown_keys(
            {"linkify": {"linkify_dir": ".linkify"}},
            {"linkify": {"linkify_md_dir": None, "linkify_html_dir": None}},
            CONFIGFILE,
        )


def test_empty_user_dict_passes():
    """An empty user dict raises no error."""
    _check_for_unknown_keys({}, {"verbose": True, "backup": {}}, CONFIGFILE)


def test_unknown_key_in_deeply_nested_dict_raises():
    """An unknown key three levels deep raises ConfigError with full path."""
    with pytest.raises(ConfigError, match="mklists.yaml.*'a.b.bad_key'"):
        _check_for_unknown_keys(
            {"a": {"b": {"bad_key": 1}}},
            {"a": {"b": {"good_key": 1}}},
            CONFIGFILE,
        )


def test_multiple_valid_keys_pass():
    """Multiple known keys at the same level raise no error."""
    _check_for_unknown_keys(
        {"verbose": True, "backup": {"backup_depth": 3}},
        {"verbose": True, "backup": {"backup_depth": 3, "backup_rootdir": None}},
        CONFIGFILE,
    )
