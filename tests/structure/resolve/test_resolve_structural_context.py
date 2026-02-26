"""Tests $MKLMKL/resolve.py

Tests function as orchestration only.
Monkeypatch `resolve_datadir_context` instead of relying on actual rule parsing.
"""

import pytest
from mklists.structure import resolve
from mklists.structure.model import DatadirStructuralContext, StructuralContext
from mklists.errors import StructureError


def test_resolve_structural_context_repo_mode(tmp_path, monkeypatch):
    """Returns StructuralContext object specifying execution context for a run."""
    configfile = tmp_path / "mklists.yaml"
    configfile.touch()

    d1 = tmp_path / "a"
    d2 = tmp_path / "b"
    d1.mkdir()
    d2.mkdir()
    (d1 / ".rules").touch()
    (d2 / ".rules").touch()

    def fake_resolve_datadir_context(**kwargs):
        return DatadirStructuralContext(
            datadir=kwargs["datadir"],
            configfile_found=None,
            configfile_used=None,
            rulefiles_found=None,
            rulefiles_used=None,
            rules=[],
        )

    monkeypatch.setattr(
        target=resolve,
        name="resolve_datadir_context",
        value=fake_resolve_datadir_context,
        raising=True,
    )

    result = resolve.resolve_structural_context(tmp_path)

    assert result == StructuralContext(
        config_rootdir=tmp_path,
        repo_configfile=tmp_path / "mklists.yaml",
        repo_rulefile=None,
        datadir_contexts=[
            DatadirStructuralContext(
                datadir=tmp_path / "a",
                configfile_found=None,
                configfile_used=None,
                rulefiles_found=None,
                rulefiles_used=None,
                rules=[],
            ),
            DatadirStructuralContext(
                datadir=tmp_path / "b",
                configfile_found=None,
                configfile_used=None,
                rulefiles_found=None,
                rulefiles_used=None,
                rules=[],
            ),
        ],
    )


def test_resolve_structural_context_no_datadirs_raises(tmp_path):
    """If no datadirs found, raises exception."""
    (tmp_path / "mklists.yaml").touch()

    with pytest.raises(StructureError):
        resolve.resolve_structural_context(tmp_path)


def test_runcontext_mixed_repo_and_local_configs(tmp_path):
    """Repo root has config, but one datadir overrides with .mklistsrc."""

    # Repo root config
    repo_configfile = tmp_path / "mklists.yaml"
    repo_configfile.touch()

    # Datadir A inherits repo config
    a = tmp_path / "a"
    a.mkdir()
    (a / ".rules").touch()

    # Datadir B overrides config
    b = tmp_path / "b"
    b.mkdir()
    (b / ".rules").touch()
    local_cfg = b / ".mklistsrc"
    local_cfg.touch()

    structural_context = resolve.resolve_structural_context(tmp_path)

    assert structural_context.repo_configfile == repo_configfile

    # find contexts
    ctx_a = next(d for d in structural_context.datadir_contexts if d.datadir == a)
    ctx_b = next(d for d in structural_context.datadir_contexts if d.datadir == b)

    assert ctx_a.configfile_used == repo_configfile
    assert ctx_b.configfile_used == local_cfg
