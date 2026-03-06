"""Tests $MKLMKL/config.py"""

import yaml
import pytest
from mklists.config.resolve import _load_merged_configdict


def test_empty_user_config_results_in_defaults(tmp_path):
    """With empty user config file, loads defaults only (without overriding)."""
    mklists_yamlfile = tmp_path / "mklists.yaml"
    mklists_yamlfile.write_text("# comment only\n")

    config = _load_merged_configdict(mklists_yamlfile)

    assert isinstance(config, dict)
    assert config


def test_no_user_config_found_uses_defaults():
    """With no user config file, loads defaults only."""
    config = _load_merged_configdict(
        configfile_used=None,
    )

    assert isinstance(config, dict)
    assert config  # not empty


def test_user_config_overrides_default(tmp_path):
    """User config file with one override."""
    mklists_yamlfile = tmp_path / "mklists.yaml"
    mklists_yamlfile.write_text("verbose: true\n")

    config = _load_merged_configdict(mklists_yamlfile)

    assert config["verbose"] is True


def test_invalid_user_yaml_raises(tmp_path):
    """Invalid user YAML fails."""
    mklists_yamlfile = tmp_path / "mklists.yaml"
    mklists_yamlfile.write_text("foo: [")

    with pytest.raises(yaml.YAMLError):
        _load_merged_configdict(mklists_yamlfile)


def test_user_yaml_must_be_mapping(tmp_path):
    """Return value must be a mapping (dictionary)."""
    mklists_yamlfile = tmp_path / "mklists.yaml"
    mklists_yamlfile.write_text("- a\n- b\n")

    with pytest.raises(TypeError):
        _load_merged_configdict(mklists_yamlfile)


def test_default_config_yaml_non_mapping_raises_type_error(mocker):
    """If DEFAULT_CONFIG_YAML decodes to a non-mapping, TypeError is raised.

    DEFAULT_CONFIG_YAML is a module-level constant that is expected to always
    decode to a dict. This branch is unreachable in normal use. The guard exists
    to catch the case where the constant is accidentally changed to non-mapping
    YAML (e.g. a bare list). This test patches the constant in the resolve
    module's namespace to trigger that branch directly.
    """
    mocker.patch("mklists.config.resolve.DEFAULT_CONFIG_YAML", "- a\n- b\n")

    with pytest.raises(TypeError, match="DEFAULT_CONFIG_YAML must decode to a mapping"):
        _load_merged_configdict(configfile_used=None)
