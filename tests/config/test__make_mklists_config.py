"""Test $MKLMKL/config.py"""

# pylint: disable=redefined-outer-name

from pathlib import Path
import re
import pytest
from mklists.config import (
    BackupConfig,
    RoutingConfig,
    SafetyConfig,
    UrlifyConfig,
    ConfigContext,
    _make_config_context,
)


@pytest.fixture
def minimal_valid_configdict():
    """Keep this up to date with DEFAULT_CONFIG_YAML."""
    return {
        "verbose": False,
        "backup": {
            "backup_enabled": False,
            "backup_rootdir": "backups",
            "backup_depth": 0,
        },
        "routing": {
            "routing_enabled": False,
            "routing_dict": {},
        },
        "safety": {
            "invalid_filename_patterns": [],
        },
        "urlify": {
            "urlify_enabled": False,
            "urlify_dir": "html",
        },
    }


def test_make_mklists_config_from_dict_success(minimal_valid_configdict, tmp_path):
    """Happy path."""
    config_context = _make_config_context(
        config_dict=minimal_valid_configdict,
        config_rootdir=tmp_path,
        configfile_used=Path("foo"),
    )

    assert isinstance(config_context, ConfigContext)
    assert config_context.backup.backup_enabled is False
    assert config_context.routing.routing_enabled is False

    assert config_context == ConfigContext(
        verbose=False,
        config_rootdir=tmp_path,
        configfile_used=Path("foo"),
        backup=BackupConfig(
            backup_enabled=False,
            backup_rootdir=tmp_path / "backups",
            backup_depth=0,
        ),
        routing=RoutingConfig(
            routing_enabled=False,
            routing_dict={},
        ),
        safety=SafetyConfig(
            invalid_filename_patterns=[],
        ),
        urlify=UrlifyConfig(
            urlify_enabled=False,
            urlify_dir=tmp_path / "html",
        ),
    )


def test_make_mklists_config_resolves_paths(minimal_valid_configdict, tmp_path):
    """Dictionary values of type Path are made absolute under config_rootdir."""
    config_context = _make_config_context(
        config_dict=minimal_valid_configdict,
        config_rootdir=tmp_path,
        configfile_used=Path("foo"),
    )

    assert config_context.backup.backup_rootdir == (tmp_path / "backups").resolve()
    assert config_context.urlify.urlify_dir == (tmp_path / "html").resolve()


def test_make_mklists_config_compiles_regexes(minimal_valid_configdict, tmp_path):
    """todo: Spot-check that one regex value is an instance of re.Pattern."""
    config_context = _make_config_context(
        config_dict=minimal_valid_configdict,
        config_rootdir=tmp_path,
        configfile_used=Path("foo"),
    )

    assert isinstance(config_context.safety.invalid_filename_patterns, list)
    # assert isinstance(config_context.safety.invalid_filename_patterns[0], re.Pattern)


def test_make_mklists_config_invalid_regex_raises(minimal_valid_configdict, tmp_path):
    """If config dict has bad regex, raises ValueError."""
    minimal_valid_configdict["safety"]["invalid_filename_patterns"] = ["["]

    with pytest.raises(ValueError):
        _make_config_context(
            config_dict=minimal_valid_configdict,
            config_rootdir=tmp_path,
            configfile_used=Path("foo"),
        )


def test_make_mklists_config_missing_required_key_raises_keyerror(
    minimal_valid_configdict, tmp_path
):
    """If config dict has missing key, raises KeyError."""
    del minimal_valid_configdict["backup"]["backup_rootdir"]

    with pytest.raises(KeyError):
        _make_config_context(
            config_dict=minimal_valid_configdict,
            config_rootdir=tmp_path,
            configfile_used=Path("foo"),
        )
