"""Tests $MKLMKL/contexts.py"""

from pathlib import Path
from mklists import contexts_datadir
from mklists.contexts_datadir import DatadirContext


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
        target=contexts_datadir,
        name="load_rules_for_datadir",
        value=fake_loader,
        raising=True,
    )

    result = contexts_datadir.resolve_datadir_context(
        datadir=datadir,
        repo_configfile=None,
        repo_rulefile=None,
    )

    expected = DatadirContext(
        datadir=datadir,
        configfile_used=local_cfg,
        rules=["R1"],
    )

    assert result == expected


def test_resolve_datadir_context_inherits_repo_config(tmp_path, monkeypatch):
    """Datadir has no .mklistsrc, so global mklists.yaml is used."""
    datadir = tmp_path
    rulefile = datadir / ".rules"
    rulefile.touch()

    repo_cfg = tmp_path / "mklists.yaml"
    repo_cfg.touch()

    monkeypatch.setattr(
        target=contexts_datadir,
        name="load_rules_for_datadir",
        value=lambda _: [],
        raising=True,
    )

    result = contexts_datadir.resolve_datadir_context(
        datadir=datadir,
        repo_configfile=repo_cfg,
        repo_rulefile=None,
    )

    expected = DatadirContext(
        datadir=datadir,
        configfile_used=repo_cfg,
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
        target=contexts_datadir,
        name="load_rules_for_datadir",
        value=fake_loader,
        raising=True,
    )

    contexts_datadir.resolve_datadir_context(
        datadir=datadir,
        repo_configfile=None,
        repo_rulefile=None,
    )

    assert captured["rulefiles"] == [datadir_rulefile]
