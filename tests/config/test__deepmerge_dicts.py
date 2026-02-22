"""Tests $MKLMKL/config.py"""


import pytest
from mklists.config import DEFAULT_CONFIG_YAML, _deepmerge_dicts


def test_deep_merge_nested_dicts():
    """Policy: recursive merge only for dictionary values."""
    base = {"a": {"b": 1, "c": 2}}
    override = {"a": {"c": 99}}
    assert _deepmerge_dicts(base, override) == {"a": {"b": 1, "c": 99}}


def test_deep_merge_lists_replace():
    """Policy: Value lists are replaced, not overridden."""
    base = {"x": [1, 2]}
    override = {"x": [9]}
    assert _deepmerge_dicts(base, override) == {"x": [9]}


def test_deep_merge_does_not_mutate_base():
    """Deep merge does not change base dictionary (from DEFAULT_YAML_STRING)."""
    base = {"a": {"b": 1}}
    override = {"a": {"b": 2}}

    result = _deepmerge_dicts(base, override)

    assert base == {"a": {"b": 1}}
    assert result == {"a": {"b": 2}}

def test_deep_merge_adds_new_keys():
    """Items only in override dictionary are added."""
    base = {"a": 1}
    override = {"b": 2}

    assert _deepmerge_dicts(base, override) == {"a": 1, "b": 2}


def test_deep_merge_adds_nested_keys():
    """Bad user config _could_ mean unsupported key is added to value dict."""
    base = {"a": {"b": 1}}
    override = {"a": {"c": 2}}

    assert _deepmerge_dicts(base, override) == {"a": {"b": 1, "c": 2}}


def test_deep_merge_dict_replaced_by_scalar():
    """Bad user config _could_ mean value dict is replaced with value scalar."""
    base = {"a": {"b": 1}}
    override = {"a": 42}

    assert _deepmerge_dicts(base, override) == {"a": 42}


def test_deep_merge_scalar_replaced_by_dict():
    """Bad user config _could_ mean value scalar is replaced with value dict."""
    base = {"a": 42}
    override = {"a": {"b": 1}}

    assert _deepmerge_dicts(base, override) == {"a": {"b": 1}}


def test_deep_merge_none_overrides_value():
    """Bad user config _could_ mean that value scalar is replaced with None."""
    base = {"a": 1}
    override = {"a": None}

    assert _deepmerge_dicts(base, override) == {"a": None}


def test_deep_merge_empty_override():
    """With empty user config, base config is simply copied."""
    base = {"a": {"b": 1}}
    override = {}

    result = _deepmerge_dicts(base, override)

    assert result == base
    assert result is not base


def test_deep_merge_empty_base():
    """Empty base yields override."""
    base = {}
    override = {"a": {"b": 1}}

    result = _deepmerge_dicts(base, override)

    assert result == override
    assert result is not override


def test_deep_merge_multiple_levels():
    """Deep nesting works recursively, not just one level deep."""
    base = {"a": {"b": {"c": 1, "d": 2}}}
    override = {"a": {"b": {"d": 99}}}

    assert _deepmerge_dicts(base, override) == {
        "a": {"b": {"c": 1, "d": 99}}
    }


def test_deep_merge_nested_list_replaced():
    """Lists are always replaced, even if nested."""
    base = {"a": {"b": [1, 2]}}
    override = {"a": {"b": [9]}}

    assert _deepmerge_dicts(base, override) == {"a": {"b": [9]}}
