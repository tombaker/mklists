"""Tests for _check_for_unknown_keys and _collect_valid_keys in config/resolve.py"""

from pathlib import Path
import pytest
from mklists.config.resolve import _check_for_unknown_keys, _collect_valid_keys
from mklists.errors import ConfigError

CONFIGFILE = Path("mklists.yaml")


# ---------------------------------------------------------------------------
# _collect_valid_keys
# ---------------------------------------------------------------------------


def test_collect_valid_keys_flat():
    """Flat dict yields its keys."""
    assert _collect_valid_keys({"a": 1, "b": 2}) == ["a", "b"]


def test_collect_valid_keys_nested():
    """Nested dict yields both parent and child keys as dotted paths."""
    result = _collect_valid_keys({"linkify": {"linkify_md_dir": None, "linkify_html_dir": None}})
    assert result == ["linkify", "linkify.linkify_md_dir", "linkify.linkify_html_dir"]


def test_collect_valid_keys_deeply_nested():
    """Keys three levels deep are returned with full dotted paths."""
    result = _collect_valid_keys({"a": {"b": {"c": 1}}})
    assert result == ["a", "a.b", "a.b.c"]


# ---------------------------------------------------------------------------
# _check_for_unknown_keys — passes
# ---------------------------------------------------------------------------


def test_valid_top_level_key_passes():
    """A known top-level key raises no error."""
    _check_for_unknown_keys({"verbose": True}, {"verbose": True}, CONFIGFILE)


def test_valid_nested_key_passes():
    """A known nested key raises no error."""
    _check_for_unknown_keys(
        {"linkify": {"linkify_md_dir": None}},
        {"linkify": {"linkify_md_dir": None, "linkify_html_dir": None}},
        CONFIGFILE,
    )


def test_empty_user_dict_passes():
    """An empty user dict raises no error."""
    _check_for_unknown_keys({}, {"verbose": True, "backup": {}}, CONFIGFILE)


def test_multiple_valid_keys_pass():
    """Multiple known keys at the same level raise no error."""
    _check_for_unknown_keys(
        {"verbose": True, "backup": {"backup_depth": 3}},
        {"verbose": True, "backup": {"backup_depth": 3, "backup_rootdir": None}},
        CONFIGFILE,
    )


def test_free_form_mapping_passes():
    """Arbitrary keys inside a dict whose defaults value is empty are not flagged.

    routing_dict is defined as {} in defaults, signalling a free-form mapping.
    User-supplied filenames inside it must not be treated as unknown keys.
    """
    _check_for_unknown_keys(
        {"routing": {"routing_dict": {"abc": "/some/path", "xyz": "/other/path"}}},
        {"routing": {"routing_dict": {}}},
        CONFIGFILE,
    )


# ---------------------------------------------------------------------------
# _check_for_unknown_keys — raises, no suggestion
# ---------------------------------------------------------------------------


def test_unknown_top_level_key_raises():
    """A completely unrecognised top-level key raises ConfigError."""
    with pytest.raises(ConfigError, match="mklists.yaml.*'zzz_unknown'"):
        _check_for_unknown_keys({"zzz_unknown": 1}, {"verbose": True}, CONFIGFILE)


def test_unknown_key_in_deeply_nested_dict_raises():
    """An unknown key three levels deep raises ConfigError with full dotted path."""
    with pytest.raises(ConfigError, match="mklists.yaml.*'a.b.bad_key'"):
        _check_for_unknown_keys(
            {"a": {"b": {"bad_key": 1}}},
            {"a": {"b": {"good_key": 1}}},
            CONFIGFILE,
        )


# ---------------------------------------------------------------------------
# _check_for_unknown_keys — raises, with "did you mean?" suggestion
# ---------------------------------------------------------------------------


def test_unknown_nested_key_suggests_similar_key():
    """linkify.linkify_dir triggers suggestions for linkify_md_dir / linkify_html_dir."""
    with pytest.raises(ConfigError, match="Did you mean:.*linkify"):
        _check_for_unknown_keys(
            {"linkify": {"linkify_dir": ".linkify"}},
            {"linkify": {"linkify_md_dir": None, "linkify_html_dir": None}},
            CONFIGFILE,
        )


def test_suggestion_includes_filename():
    """Error message names the config file even when a suggestion is present."""
    with pytest.raises(ConfigError, match="mklists.yaml"):
        _check_for_unknown_keys(
            {"linkify": {"linkify_dir": ".linkify"}},
            {"linkify": {"linkify_md_dir": None, "linkify_html_dir": None}},
            CONFIGFILE,
        )
