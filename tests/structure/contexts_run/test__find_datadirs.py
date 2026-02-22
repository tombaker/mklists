"""Tests $MKLSTRUCTURE/contexts_run.py"""

import pytest
from mklists.structure.contexts_run import _find_datadirs


def test_find_datadirs_finds_directories_with_rules(tmp_path):
    """Find directories that have a `.rules` file."""
    d1 = tmp_path / "a"
    d2 = tmp_path / "b"
    d3 = tmp_path / "c"

    d1.mkdir()
    d2.mkdir()
    d3.mkdir()

    (d1 / ".rules").write_text("rules")
    (d3 / ".rules").write_text("rules")

    result = list(_find_datadirs(tmp_path))

    assert result == [d1, d3]


def test_find_datadirs_ignores_directories_without_rules(tmp_path):
    """Ignores directories that have no `.rules` file."""
    d1 = tmp_path / "a"
    d2 = tmp_path / "b"

    d1.mkdir()
    d2.mkdir()

    (d1 / ".rules").write_text("rules")

    result = list(_find_datadirs(tmp_path))

    assert result == [d1]


def test_find_datadirs_sorted(tmp_path):
    """Lists directories in sort order."""
    d1 = tmp_path / "b"
    d2 = tmp_path / "a"

    d1.mkdir()
    d2.mkdir()

    (d1 / ".rules").write_text("rules")
    (d2 / ".rules").write_text("rules")

    result = list(_find_datadirs(tmp_path))

    assert result == [d2, d1]


def test_find_datadirs_empty(tmp_path):
    """Returns empty list if none found."""
    assert _find_datadirs(tmp_path) == []


def test_finds_datadirs_with_rules_file_not_directory(tmp_path):
    """For datadir to be found, `.rules` must be a file, not a directory."""
    d = tmp_path / "a" / ".rules"
    d.mkdir(parents=True)

    result = list(_find_datadirs(tmp_path))

    assert result == []


def test_find_datadirs_in_toplevel_directories_only(tmp_path):
    """For datadir to be found, `.rules` must be in a top-level directory."""
    d = tmp_path / "a" / "b"
    d.mkdir(parents=True)

    (d / ".rules").write_text("rules")

    result = list(_find_datadirs(tmp_path))

    assert result == []


def test_finds_datadirs_even_in_hidden_directories(tmp_path):
    """Edge case: will find `.rules` even in hidden directories.

    FYI: It should in practice never happen that a user creates a hidden 
    data directory, but it seems excessive for `_find_datadirs` to explicitly
    guard against this.
    """
    d = tmp_path / ".a"
    d.mkdir(parents=True)

    (d / ".rules").write_text("rules")

    result = list(_find_datadirs(tmp_path))

    assert result == [d]
