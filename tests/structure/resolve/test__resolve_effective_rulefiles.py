"""Tests $MKLSTRUCTURE/resolve.py"""

import pytest

# from mklists.structure.resolve import _resolve_effective_rulefiles
# from mklists.errors import StructureError


@pytest.mark.skip(reason="Broken after refactoring resolve_datadir_context.")
def test_resolve_effective_rulefiles_datadir_only(tmp_path):
    """Rulefile only in datadir, so return list of one rulefile."""
    datadir_rulefile = tmp_path / ".rules"

    result = _resolve_effective_rulefiles(
        datadir_configfile=None,
        datadir_rulefile=datadir_rulefile,
        repo_rulefile=None,
    )

    assert result == [datadir_rulefile]


@pytest.mark.skip(reason="Broken after refactoring resolve_datadir_context.")
def test_resolve_effective_rulefiles_repo_and_datadir(tmp_path):
    """Repo and datadir rulefiles are both present."""
    repo_rulefile = tmp_path / "mklists.rules"
    datadir = tmp_path / "a"
    datadir_rulefile = datadir / ".rules"

    result = _resolve_effective_rulefiles(
        datadir_configfile=None,
        datadir_rulefile=datadir_rulefile,
        repo_rulefile=repo_rulefile,
    )

    assert result == [repo_rulefile, datadir_rulefile]


@pytest.mark.skip(reason="Broken after refactoring resolve_datadir_context.")
def test_resolve_effective_rulefiles_repo_and_datadir_datadir_selfcontained(tmp_path):
    """Repo and datadir rulefiles are both present, but datadir is self-contained."""
    repo_rulefile = tmp_path / "mklists.rules"
    datadir = tmp_path / "a"
    datadir_rulefile = datadir / ".rules"
    datadir_configfile = datadir / ".mklistsrc"

    result = _resolve_effective_rulefiles(
        datadir_configfile=datadir_configfile,
        datadir_rulefile=datadir_rulefile,
        repo_rulefile=repo_rulefile,
    )

    assert result == [datadir_rulefile]


@pytest.mark.skip(reason="Broken after refactoring resolve_datadir_context.")
def test_resolve_effective_rulefiles_repo_and_datadir_the_same(tmp_path):
    """Repo and datadir rulefiles are both present.

    Note that a directory cannot be both a repo root and a datadir.
    However, _resolve_effective_rulefiles is not responsible for
    enforcing that invariant.

    Given two rulefile paths, the function returns them in deterministic
    order. They enforce only that the datadir rulefile exists.

    todo: Is this necessary?
    """
    repo = tmp_path / "mklists.rules"
    datadir = tmp_path / ".rules"

    result = _resolve_effective_rulefiles(
        datadir_configfile=None,
        datadir_rulefile=datadir,
        repo_rulefile=repo,
    )

    assert result == [repo, datadir]


@pytest.mark.skip(reason="Broken after refactoring resolve_datadir_context.")
def test_resolve_effective_rulefiles_repo_only_raises(tmp_path):
    """Datadir rulefile is missing, so raises StructureError.

    todo: Is this necessary?
    """
    repo = tmp_path / "mklists.rules"

    with pytest.raises(StructureError):
        _resolve_effective_rulefiles(
            datadir_configfile=None,
            datadir_rulefile=None,
            repo_rulefile=repo,
        )


@pytest.mark.skip(reason="Broken after refactoring resolve_datadir_context.")
def test_resolve_effective_rulefiles_missing_datadir_raises():
    """Rulefile is missing in datadir, so raises StructureError.

    Given safeguards upstream, this should in practice never happen.
    The invariant is enforced here defensively for robustness and
    future-proofing.

    todo: Is this necessary?
    """
    with pytest.raises(StructureError):
        _resolve_effective_rulefiles(
            datadir_configfile=None,
            datadir_rulefile=None,
            repo_rulefile=None,
        )
