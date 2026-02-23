"""@@@"""

# pylint: disable=redefined-outer-name


import pytest
from mklists.config import (
    BackupSettings,
    RoutingConfig,
    SafetyConfig,
    UrlifyConfig,
    SettingsContext,
    _make_mklists_config,
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
    mklists_cfg = _make_mklists_config(
        minimal_valid_configdict,
        config_rootdir=tmp_path,
    )

    assert isinstance(mklists_cfg, SettingsContext)
    assert mklists_cfg.backup.backup_enabled is False
    assert mklists_cfg.routing.routing_enabled is False

    assert mklists_cfg == SettingsContext(
        verbose=False,
        backup=BackupSettings(
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
    mklists_cfg = _make_mklists_config(
        minimal_valid_configdict, config_rootdir=tmp_path
    )

    assert mklists_cfg.backup.backup_rootdir == (tmp_path / "backups").resolve()
    assert mklists_cfg.urlify.urlify_dir == (tmp_path / "html").resolve()


def test_make_mklists_config_compiles_regexes(minimal_valid_configdict, tmp_path):
    """Spot-check that one regex value is an instance of re.Pattern."""
    mklists_cfg = _make_mklists_config(
        minimal_valid_configdict,
        config_rootdir=tmp_path,
    )

    assert isinstance(mklists_cfg.safety.invalid_filename_patterns, list)


def test_make_mklists_config_invalid_regex_raises(minimal_valid_configdict, tmp_path):
    """If config dict has bad regex, raises ValueError."""
    minimal_valid_configdict["safety"]["invalid_filename_patterns"] = ["["]

    with pytest.raises(ValueError):
        _make_mklists_config(minimal_valid_configdict, config_rootdir=tmp_path)


def test_make_mklists_config_missing_required_key_raises_keyerror(
    minimal_valid_configdict, tmp_path
):
    """If config dict has missing key, raises KeyError."""
    del minimal_valid_configdict["backup"]["backup_rootdir"]

    with pytest.raises(KeyError):
        _make_mklists_config(
            minimal_valid_configdict,
            config_rootdir=tmp_path,
        )
