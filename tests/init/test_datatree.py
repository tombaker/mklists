"""Tests for src/mklists/init/datatree.py"""

import pytest

from mklists.config.defaults import DEFAULT_CONFIG_YAML
from mklists.errors import InitError
from mklists.init.datadir import EXAMPLE_RULES
from mklists.init.datatree import init_datatree


# ── directory structure ───────────────────────────────────────────────────────


def test_creates_path_if_not_exists(tmp_path):
    """Creates the target directory if it does not yet exist."""
    new_dir = tmp_path / "newdir"
    init_datatree(new_dir)
    assert new_dir.is_dir()


def test_creates_no_subdirs(tmp_path):
    """Never creates any datadir subdirectories."""
    init_datatree(tmp_path)
    subdirs = [p for p in tmp_path.iterdir() if p.is_dir()]
    assert subdirs == []


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


def test_mklists_rules_has_example_content(tmp_path):
    """mklists.rules is always populated with EXAMPLE_RULES."""
    init_datatree(tmp_path)
    assert (tmp_path / "mklists.rules").read_text() == EXAMPLE_RULES


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


def test_conflict_prevents_all_writes(tmp_path):
    """All-or-nothing: if a conflict is detected, no files are written."""
    (tmp_path / "mklists.yaml").write_text("")
    with pytest.raises(InitError):
        init_datatree(tmp_path)
    assert not (tmp_path / "mklists.rules").exists()
