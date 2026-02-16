"""Tests $MKLMKL/contexts.py"""

# pylint: disable=missing-function-docstring,import-outside-toplevel
# pylint: disable=redefined-outer-name,unused-argument

import pytest
#from mklists.datadirs import DatadirContext


def touch(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("")


@pytest.fixture
def fake_rule_loader(monkeypatch):
    """Stub out rule parsing for planner tests.

    resolve_datadir_contexts() normally calls load_rules_from_files() to
    parse and validate rule files.  The tests in this module only
    needs to know _which_ files would be selected, not their contents.

    This fixture replaces (ie "monkeypatches") the function
    `contexts.load_rules_for_datadir` with a simple function that returns
    the filenames it receives.  The planner can then be verified without
    invoking regex compilation, filename validation, or rulechain checks.

    `monkeypatch.setattr` modifies the attribute _as looked up by the
    module under test_.  Since `resolve_datadir_contexts` refers to
    `load_rules_for_datadir` by way of the `mklists.contexts` module namespace,
    it is that exact object that is patched (`contexts.load_rules_for_datadir`),
    not the original function defined in `mklists.rules`.
    """
    from mklists import contexts

    def _fake(paths):
        return [p.name for p in paths]

    monkeypatch.setattr(contexts, "load_rules_for_datadir", _fake)


@pytest.mark.skip
def test_repo_root_discovers_datadirs(tmp_path, fake_rule_loader):
    """Discovers two datadirs under startdir `Path(repo)`."""
    from mklists import contexts

    repo = tmp_path
    touch(repo / "mklists.yaml")
    d1 = repo / "d1"
    d2 = repo / "d2"
    touch(d1 / ".rules")
    touch(d2 / ".rules")

    result = contexts.resolve_datadir_contexts(repo)

    assert result == [
        DatadirContext(
            datadir_path=d1,
            configfile_path=repo / "mklists.yaml",
            rules=[".rules"],  # fake placeholder output
        ),
        DatadirContext(
            datadir_path=d2,
            configfile_path=repo / "mklists.yaml",
            rules=[".rules"],  # fake placeholder output
        ),
    ]

    assert {c.datadir_path for c in result} == {d1, d2}


@pytest.mark.skip
def test_startdir_is_single_datadir(tmp_path, fake_rule_loader):
    """Returns list with just one datadir under startdir `Path(d)`."""
    from mklists import contexts

    d = tmp_path
    touch(d / ".rules")

    result = contexts.resolve_datadir_contexts(d)

    assert result == [
        DatadirContext(
            datadir_path=d,
            configfile_path=None,
            rules=[".rules"],  # fake placeholder output
        ),
    ]


@pytest.mark.skip
def test_datadir_inherits_repo_rules(tmp_path, fake_rule_loader):
    """Fake output shows that datadir inherits repo rules when found."""
    from mklists import contexts

    repo = tmp_path
    touch(repo / "mklists.yaml")
    touch(repo / "mklists.rules")

    d = repo / "data"
    touch(d / ".rules")

    result = contexts.resolve_datadir_contexts(repo)

    assert result == [
        DatadirContext(
            datadir_path=d,
            configfile_path=repo / "mklists.yaml",
            rules=["mklists.rules", ".rules"],  # fake placeholder output
        ),
    ]


@pytest.mark.skip
def test_selfcontained_datadir_no_inherit(tmp_path, fake_rule_loader):
    """Fake output shows datadir does not inherit repo rules when none are found."""
    from mklists import contexts

    repo = tmp_path
    touch(repo / "mklists.yaml")
    touch(repo / "mklists.rules")

    d = repo / "data"
    touch(d / ".rules")
    touch(d / ".mklistsrc")

    result = contexts.resolve_datadir_contexts(repo)

    assert result == [
        DatadirContext(
            datadir_path=d,
            configfile_path=repo / "data" / ".mklistsrc",
            rules=[".rules"],  # fake placeholder output
        ),
    ]


@pytest.mark.skip
def test_dir_cannot_be_repo_and_datadir(tmp_path):
    """Starting directory cannot be both Repo Root and Datadir."""
    from mklists import contexts

    touch(tmp_path / "mklists.yaml")
    touch(tmp_path / ".rules")

    with pytest.raises(RuntimeError):
        contexts.resolve_datadir_contexts(tmp_path)


@pytest.mark.skip
def test_invalid_startdir(tmp_path):
    """Starting directory cannot be both Repo Root and Datadir."""
    from mklists import contexts

    with pytest.raises(RuntimeError):
        contexts.resolve_datadir_contexts(tmp_path)
