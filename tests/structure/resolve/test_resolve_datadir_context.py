"""Tests $MKLSTRUCTURE/contexts.py"""

from pathlib import Path
import pytest
from mklists.structure import resolve
from mklists.structure.resolve import DatadirStructuralContext


def test_rulefiles_found_differs_from_used_when_local_configfile_found(
    tmp_path, monkeypatch
):
    """Local and repo rulefiles are discovered in self-contained, only local used."""
    datadir = tmp_path

    local_configfile = datadir / ".mklistsrc"
    local_configfile.touch()

    local_rulefile = datadir / ".rules"
    local_rulefile.touch()

    repo_rulefile = tmp_path / "mklists.rules"
    repo_rulefile.touch()

    monkeypatch.setattr(
        target=resolve,
        name="load_rules_for_datadir",
        value=lambda _: [],
        raising=True,
    )

    result = resolve.resolve_datadir_context(
        datadir=datadir,
        repo_configfile=None,
        repo_rulefile=repo_rulefile,
    )

    # Structural invariant
    assert result.rulefiles_found != result.rulefiles_used

    # More precise expectations
    assert result.rulefiles_found == [repo_rulefile, local_rulefile]
    assert result.rulefiles_used == [local_rulefile]


def test_resolve_datadir_context_local_config_and_rules(tmp_path, monkeypatch):
    """Datadir has its own config and rulefile."""
    datadir = tmp_path
    local_cfg = datadir / ".mklistsrc"
    local_rule = datadir / ".rules"

    local_cfg.touch()
    local_rule.touch()

    def fake_loader(_rulefiles: list[Path]):
        """Test double for load_rules_for_datadir.

        Returns fixed value to isolate resolve_datadir_context
        from rule parsing logic.

        The real function returns list[Rule].

        The parameter `rulefiles` is retained to match the real
        signature, but it is prefixed with `_` to signal that it
        is intentionally unused in this test.
        """
        return ["R1"]

    monkeypatch.setattr(
        target=resolve,
        name="load_rules_for_datadir",
        value=fake_loader,
        raising=True,
    )

    result = resolve.resolve_datadir_context(
        datadir=datadir,
        repo_configfile=None,
        repo_rulefile=None,
    )

    expected = DatadirStructuralContext(
        datadir=datadir,
        configfile_found=local_cfg,
        configfile_used=local_cfg,
        rulefiles_found=[local_rule],
        rulefiles_used=[local_rule],
        rules=["R1"],
    )

    assert result == expected


def test_resolve_datadir_context_inherits_repo_config(tmp_path, monkeypatch):
    """Datadir has no .mklistsrc, so global mklists.yaml is used."""
    datadir = tmp_path
    rulefile = datadir / ".rules"
    rulefile.touch()

    repo_configfile = tmp_path / "mklists.yaml"
    repo_configfile.touch()

    monkeypatch.setattr(
        target=resolve,
        name="load_rules_for_datadir",
        value=lambda _: [],
        raising=True,
    )

    result = resolve.resolve_datadir_context(
        datadir=datadir,
        repo_configfile=repo_configfile,
        repo_rulefile=None,
    )

    expected = DatadirStructuralContext(
        datadir=datadir,
        configfile_found=None,
        configfile_used=repo_configfile,
        rulefiles_found=[rulefile],
        rulefiles_used=[rulefile],
        rules=[],
    )

    assert result == expected


def test_resolve_datadir_context_passes_rulefiles_to_loader(tmp_path, monkeypatch):
    """Resolved rulefile list is passed to rule loader."""
    datadir = tmp_path
    datadir_rulefile = datadir / ".rules"
    datadir_rulefile.touch()

    captured: dict[str, list[Path]] = {}

    def fake_loader(rulefiles: list[Path]) -> list:
        captured["rulefiles"] = rulefiles
        return []

    monkeypatch.setattr(
        target=resolve,
        name="load_rules_for_datadir",
        value=fake_loader,
        raising=True,
    )

    resolve.resolve_datadir_context(
        datadir=datadir,
        repo_configfile=None,
        repo_rulefile=None,
    )

    assert captured["rulefiles"] == [datadir_rulefile]
