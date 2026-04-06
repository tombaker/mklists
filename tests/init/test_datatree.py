"""Tests for src/mklists/init/datatree.py"""

import pytest

from mklists.config.defaults import DEFAULT_CONFIG_YAML
from mklists.errors import InitError
from mklists.init.datadir import EXAMPLE_RULES
from mklists.init.datatree import init_datatree


# ── directory structure ───────────────────────────────────────────────────────


def test_creates_default_subdirs(tmp_path):
    """Always creates default subdirectories a/ and b/."""
    init_datatree(tmp_path)
    assert (tmp_path / "a").is_dir()
    assert (tmp_path / "b").is_dir()


def test_creates_custom_subdirs(tmp_path):
    """Creates subdirectories named by the datadirs parameter."""
    init_datatree(tmp_path, datadirs=("x", "y", "z"))
    assert (tmp_path / "x").is_dir()
    assert (tmp_path / "y").is_dir()
    assert (tmp_path / "z").is_dir()


def test_creates_path_if_not_exists(tmp_path):
    """Creates the target directory if it does not yet exist."""
    new_dir = tmp_path / "newdir"
    init_datatree(new_dir)
    assert new_dir.is_dir()


# ── mklists.yaml ──────────────────────────────────────────────────────────────


def test_creates_mklists_yaml(tmp_path):
    """Always creates mklists.yaml."""
    init_datatree(tmp_path)
    assert (tmp_path / "mklists.yaml").exists()


def test_mklists_yaml_contains_default_config(tmp_path):
    """mklists.yaml is always populated with DEFAULT_CONFIG_YAML."""
    init_datatree(tmp_path)
    assert (tmp_path / "mklists.yaml").read_text() == DEFAULT_CONFIG_YAML


# ── mklists.rules ─────────────────────────────────────────────────────────────


def test_creates_mklists_rules(tmp_path):
    """Always creates mklists.rules."""
    init_datatree(tmp_path)
    assert (tmp_path / "mklists.rules").exists()


def test_mklists_rules_is_empty_by_default(tmp_path):
    """Without rules=True, mklists.rules is empty."""
    init_datatree(tmp_path)
    assert (tmp_path / "mklists.rules").read_text() == ""


def test_rules_flag_populates_mklists_rules(tmp_path):
    """With rules=True, mklists.rules contains example content."""
    init_datatree(tmp_path, rules=True)
    assert (tmp_path / "mklists.rules").read_text() == EXAMPLE_RULES


# ── subdir .rules files ───────────────────────────────────────────────────────


def test_creates_subdir_rules_files(tmp_path):
    """Always creates .rules in each subdir."""
    init_datatree(tmp_path)
    assert (tmp_path / "a" / ".rules").exists()
    assert (tmp_path / "b" / ".rules").exists()


def test_subdir_rules_files_empty_by_default(tmp_path):
    """Without rules=True, subdir .rules files are empty."""
    init_datatree(tmp_path)
    assert (tmp_path / "a" / ".rules").read_text() == ""
    assert (tmp_path / "b" / ".rules").read_text() == ""


def test_rules_flag_populates_all_rules_files(tmp_path):
    """With rules=True, all rule files contain example content."""
    init_datatree(tmp_path, rules=True)
    assert (tmp_path / "mklists.rules").read_text() == EXAMPLE_RULES
    assert (tmp_path / "a" / ".rules").read_text() == EXAMPLE_RULES
    assert (tmp_path / "b" / ".rules").read_text() == EXAMPLE_RULES


# ── conflict detection ────────────────────────────────────────────────────────


def test_raises_if_rules_file_exists(tmp_path):
    """Raises InitError if .rules already exists."""
    (tmp_path / ".rules").write_text("")
    with pytest.raises(InitError):
        init_datatree(tmp_path)


def test_raises_if_mklistsrc_exists(tmp_path):
    """Raises InitError if .mklistsrc already exists."""
    (tmp_path / ".mklistsrc").write_text("")
    with pytest.raises(InitError):
        init_datatree(tmp_path)


def test_raises_if_mklists_yaml_exists(tmp_path):
    """Raises InitError if mklists.yaml already exists."""
    (tmp_path / "mklists.yaml").write_text("")
    with pytest.raises(InitError):
        init_datatree(tmp_path)


def test_raises_if_mklists_rules_exists(tmp_path):
    """Raises InitError if mklists.rules already exists."""
    (tmp_path / "mklists.rules").write_text("")
    with pytest.raises(InitError):
        init_datatree(tmp_path)


def test_raises_if_named_subdir_exists(tmp_path):
    """Raises InitError if a named subdir already exists."""
    (tmp_path / "a").mkdir()
    with pytest.raises(InitError):
        init_datatree(tmp_path)


def test_conflict_prevents_all_writes(tmp_path):
    """All-or-nothing: if a conflict is detected, no files are written."""
    (tmp_path / "a").mkdir()
    with pytest.raises(InitError):
        init_datatree(tmp_path)
    assert not (tmp_path / "mklists.yaml").exists()
    assert not (tmp_path / "mklists.rules").exists()
    assert not (tmp_path / "b").exists()
