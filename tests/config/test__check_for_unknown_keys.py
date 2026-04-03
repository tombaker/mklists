"""Tests for _check_for_unknown_keys in mklists/config/resolve.py"""

import pytest
from mklists.config.resolve import _check_for_unknown_keys
from mklists.errors import ConfigError


def test_valid_top_level_key_passes():
    """A known top-level key raises no error."""
    _check_for_unknown_keys({"verbose": True}, {"verbose": True})


def test_unknown_top_level_key_raises():
    """An unknown top-level key raises ConfigError."""
    with pytest.raises(ConfigError, match="'linkify_dir'"):
        _check_for_unknown_keys({"linkify_dir": ".linkify"}, {"linkify": {}})


def test_valid_nested_key_passes():
    """A known nested key raises no error."""
    _check_for_unknown_keys(
        {"linkify": {"linkify_md_dir": None}},
        {"linkify": {"linkify_md_dir": None, "linkify_html_dir": None}},
    )


def test_unknown_nested_key_raises():
    """An unknown nested key raises ConfigError with dot-separated path."""
    with pytest.raises(ConfigError, match="'linkify.linkify_dir'"):
        _check_for_unknown_keys(
            {"linkify": {"linkify_dir": ".linkify"}},
            {"linkify": {"linkify_md_dir": None, "linkify_html_dir": None}},
        )


def test_empty_user_dict_passes():
    """An empty user dict raises no error."""
    _check_for_unknown_keys({}, {"verbose": True, "backup": {}})


def test_unknown_key_in_deeply_nested_dict_raises():
    """An unknown key three levels deep raises ConfigError with full path."""
    with pytest.raises(ConfigError, match="'a.b.bad_key'"):
        _check_for_unknown_keys(
            {"a": {"b": {"bad_key": 1}}},
            {"a": {"b": {"good_key": 1}}},
        )


def test_multiple_valid_keys_pass():
    """Multiple known keys at the same level raise no error."""
    _check_for_unknown_keys(
        {"verbose": True, "backup": {"backup_depth": 3}},
        {"verbose": True, "backup": {"backup_depth": 3, "backup_rootdir": None}},
    )
