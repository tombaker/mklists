"""Tests $MKLMKL/contexts_run.py

Tests function as orchestration only.
Monkeypatch `resolve_datadir_context` instead of relying on actual rule parsing.
"""

import pytest
from mklists import contexts_run
from mklists.contexts_datadir import DatadirContext
from mklists.contexts_run import RunContext
from mklists.errors import StructureError


def test_resolve_run_context_repo_mode(tmp_path, monkeypatch):
    """Returns RunContext object specifying execution context for a run."""
    configfile = tmp_path / "mklists.yaml"
    configfile.touch()

    d1 = tmp_path / "a"
    d2 = tmp_path / "b"
    d1.mkdir()
    d2.mkdir()
    (d1 / ".rules").touch()
    (d2 / ".rules").touch()

    def fake_resolve_datadir_context(**kwargs):
        return DatadirContext(
            datadir=kwargs["datadir"],
            configfile_used=None,
            rules=[],
        )

    monkeypatch.setattr(
        target=contexts_run,
        name="resolve_datadir_context",
        value=fake_resolve_datadir_context,
        raising=True,
    )

    result = contexts_run.resolve_run_context(tmp_path)

    assert result == RunContext(
        rundir=tmp_path,
        repo_configfile=tmp_path / "mklists.yaml",
        repo_rulefile=None,
        datadir_contexts=[
            DatadirContext(datadir=tmp_path / "a", configfile_used=None, rules=[]),
            DatadirContext(datadir=tmp_path / "b", configfile_used=None, rules=[]),
        ],
    )


def test_resolve_run_context_no_datadirs_raises(tmp_path):
    """If no datadirs found, raises exception."""
    (tmp_path / "mklists.yaml").touch()

    with pytest.raises(StructureError):
        contexts_run.resolve_run_context(tmp_path)
