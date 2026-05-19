"""Tests for src/mklists/init/datadir.py"""

import pytest

from mklists.config.defaults import DEFAULT_CONFIG_YAML
from mklists.errors import InitError
from mklists.init.datadir import EXAMPLE_RULES, init_datadir


# ── .rules file ──────────────────────────────────────────────────────────────


def test_creates_rules_file(tmp_path):
    """Always creates .rules regardless of flags."""
    init_datadir(tmp_path)
    assert (tmp_path / ".rules").exists()


def test_rules_file_has_example_content_by_default(tmp_path):
    """By default, .rules contains example content."""
    init_datadir(tmp_path)
    assert (tmp_path / ".rules").read_text() == EXAMPLE_RULES


def test_bare_creates_empty_rules_file(tmp_path):
    """With bare=True, .rules is empty."""
    init_datadir(tmp_path, bare=True)
    assert (tmp_path / ".rules").read_text() == ""


# ── .mklistsrc file ───────────────────────────────────────────────────────────


def test_no_mklistsrc_by_default(tmp_path):
    """Without --self-contained, .mklistsrc is not created."""
    init_datadir(tmp_path)
    assert not (tmp_path / ".mklistsrc").exists()


def test_self_contained_creates_mklistsrc(tmp_path):
    """With self_contained=True, .mklistsrc is created."""
    init_datadir(tmp_path, self_contained=True)
    assert (tmp_path / ".mklistsrc").exists()


def test_self_contained_mklistsrc_contains_default_config(tmp_path):
    """Created .mklistsrc is populated with DEFAULT_CONFIG_YAML."""
    init_datadir(tmp_path, self_contained=True)
    assert (tmp_path / ".mklistsrc").read_text() == DEFAULT_CONFIG_YAML


def test_bare_self_contained_creates_empty_mklistsrc(tmp_path):
    """With bare=True and self_contained=True, .mklistsrc is empty."""
    init_datadir(tmp_path, bare=True, self_contained=True)
    assert (tmp_path / ".mklistsrc").read_text() == ""


# ── path creation ─────────────────────────────────────────────────────────────


def test_creates_path_if_not_exists(tmp_path):
    """Creates the target directory if it does not yet exist."""
    new_dir = tmp_path / "newdir"
    init_datadir(new_dir)
    assert new_dir.is_dir()
    assert (new_dir / ".rules").exists()


# ── conflict detection ────────────────────────────────────────────────────────


def test_raises_if_rules_file_exists(tmp_path):
    """Raises InitError if .rules already exists."""
    (tmp_path / ".rules").write_text("")
    with pytest.raises(InitError):
        init_datadir(tmp_path)


def test_raises_if_mklistsrc_exists(tmp_path):
    """Raises InitError if .mklistsrc already exists."""
    (tmp_path / ".mklistsrc").write_text("")
    with pytest.raises(InitError):
        init_datadir(tmp_path)


def test_raises_if_mklists_yaml_exists(tmp_path):
    """Raises InitError if mklists.yaml already exists (datatree marker)."""
    (tmp_path / "mklists.yaml").write_text("")
    with pytest.raises(InitError):
        init_datadir(tmp_path)


def test_raises_if_mklists_rules_exists(tmp_path):
    """Raises InitError if mklists.rules already exists (datatree marker)."""
    (tmp_path / "mklists.rules").write_text("")
    with pytest.raises(InitError):
        init_datadir(tmp_path)


def test_conflict_prevents_all_writes(tmp_path):
    """All-or-nothing: if a conflict is detected, no files are written."""
    (tmp_path / "mklists.yaml").write_text("")
    with pytest.raises(InitError):
        init_datadir(tmp_path, self_contained=True)
    assert not (tmp_path / ".rules").exists()
    assert not (tmp_path / ".mklistsrc").exists()
