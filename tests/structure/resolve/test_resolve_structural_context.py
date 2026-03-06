"""Tests $MKLMKL/structure/resolve.py"""

import pytest
from mklists.errors import StructureError
from mklists.structure.markers import (
    DATADIR_CONFIGFILE_NAME,
    DATADIR_RULEFILE_NAME,
    REPO_CONFIGFILE_NAME,
    REPO_RULEFILE_NAME,
)
from mklists.structure.model import (
    DatadirStructuralContext,
    StartdirStructuralContext,
    StructuralContext,
)
from mklists.structure.resolve import resolve_structural_context


# ─── Error conditions ─────────────────────────────────────────

def test_raises_when_startdir_has_no_markers(tmp_path):
    """Raises if startdir has no repo or datadir markers."""
    with pytest.raises(StructureError):
        resolve_structural_context(tmp_path)


@pytest.mark.parametrize(
    "repo_marker",
    [REPO_CONFIGFILE_NAME, REPO_RULEFILE_NAME],
)
def test_raises_when_startdir_is_both_repo_root_and_datadir(tmp_path, repo_marker):
    """Raises if startdir has both repo marker and datadir marker (ie, .rules)."""
    (tmp_path / repo_marker).touch()
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    with pytest.raises(StructureError):
        resolve_structural_context(tmp_path)


def test_raises_when_repo_root_has_no_datadirs(tmp_path):
    """Raises if startdir is repo root but no datadirs exist under it."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()

    with pytest.raises(StructureError):
        resolve_structural_context(tmp_path)


def test_raises_when_repo_root_subdirs_have_no_rules_file(tmp_path):
    """Raises if repo root has subdirectories but none contain .rules."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    (tmp_path / "nodata").mkdir()

    with pytest.raises(StructureError, match="No datadirs found"):
        resolve_structural_context(tmp_path)


def test_returns_structural_context_instance(tmp_path):
    """Returns StructuralContext instance."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    assert isinstance(resolve_structural_context(tmp_path), StructuralContext)


# ─── Basic return types ───────────────────────────────────────


def test_startdir_context_type(tmp_path):
    """startdir_context field is StartdirStructuralContext instance."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    structural_context = resolve_structural_context(tmp_path)

    assert isinstance(structural_context.startdir_context, StartdirStructuralContext)


def test_datadir_contexts_type(tmp_path):
    """Each element in datadir_contexts is a DatadirStructuralContext instance."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    structural_context = resolve_structural_context(tmp_path)

    for ctx in structural_context.datadir_contexts:
        assert isinstance(ctx, DatadirStructuralContext)


def test_accepts_string_path(tmp_path):
    """Accepts path as string, not just Path object."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    structural_context = resolve_structural_context(str(tmp_path))

    assert isinstance(structural_context, StructuralContext)


# ─── Repo root: startdir has mklists.yaml or mklists.rules ───────────────────


@pytest.mark.parametrize(
    "repo_marker",
    [REPO_CONFIGFILE_NAME, REPO_RULEFILE_NAME],
)
def test_repo_root_with_one_datadir(tmp_path, repo_marker):
    """Repo root with one datadir returns one datadir context."""
    (tmp_path / repo_marker).touch()
    d = tmp_path / "data"
    d.mkdir()
    (d / DATADIR_RULEFILE_NAME).touch()

    structural_context = resolve_structural_context(tmp_path)

    assert len(structural_context.datadir_contexts) == 1
    assert structural_context.datadir_contexts[0].datadir == d


def test_repo_root_is_repo_root(tmp_path):
    """If repo root, is_repo_root is True."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    d = tmp_path / "data"
    d.mkdir()
    (d / DATADIR_RULEFILE_NAME).touch()

    structural_context = resolve_structural_context(tmp_path)

    assert structural_context.startdir_context.is_repo_root is True


def test_repo_root_config_rootdir_is_startdir(tmp_path):
    """If repo root, config_rootdir equals startdir."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    d = tmp_path / "data"
    d.mkdir()
    (d / DATADIR_RULEFILE_NAME).touch()

    structural_context = resolve_structural_context(tmp_path)

    assert structural_context.startdir_context.config_rootdir == tmp_path


def test_repo_root_datadirs_sorted(tmp_path):
    """Datadirs discovered from repo root are sorted alphabetically by name."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    for name in ["c", "a", "b"]:
        d = tmp_path / name
        d.mkdir()
        (d / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert [ctx.datadir.name for ctx in result.datadir_contexts] == ["a", "b", "c"]


def test_repo_root_multiple_datadirs_all_included(tmp_path):
    """All datadirs under repo root listed in context."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    for name in ["alpha", "beta"]:
        d = tmp_path / name
        d.mkdir()
        (d / DATADIR_RULEFILE_NAME).touch()

    context = resolve_structural_context(tmp_path)

    assert len(context.datadir_contexts) == 2


def test_repo_root_includes_selfcontained_datadirs(tmp_path):
    """All datadirs under repo root, even if self-contained, listed in context."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    for name in ["alpha", "beta"]:
        d = tmp_path / name
        d.mkdir()
        (d / DATADIR_RULEFILE_NAME).touch()
    (tmp_path / "alpha" / DATADIR_CONFIGFILE_NAME).touch()

    context = resolve_structural_context(tmp_path)

    assert len(context.datadir_contexts) == 2


def test_repo_root_datadir_rulefile_path(tmp_path):
    """datadir_rulefile points to .rules file in given datadir."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    d = tmp_path / "data"
    d.mkdir()
    (d / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert result.datadir_contexts[0].datadir_rulefile == d / DATADIR_RULEFILE_NAME


def test_repo_root_datadir_without_configfile(tmp_path):
    """Datadir lacking .mklistsrc has datadir_configfile_found=None."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    d = tmp_path / "data"
    d.mkdir()
    (d / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert result.datadir_contexts[0].datadir_configfile_found is None


def test_repo_root_datadir_with_configfile(tmp_path):
    """Datadir with .mklistsrc has datadir_configfile_found set to its path."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    d = tmp_path / "data"
    d.mkdir()
    (d / DATADIR_RULEFILE_NAME).touch()
    (d / DATADIR_CONFIGFILE_NAME).touch()

    structural_context = resolve_structural_context(tmp_path)

    assert structural_context.datadir_contexts[0].datadir_configfile_found == (
        d / DATADIR_CONFIGFILE_NAME
    )


def test_repo_root_subdirs_without_rules_are_excluded(tmp_path):
    """Subdirectories that lack .rules are not included as datadirs."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    included = tmp_path / "yes"
    included.mkdir()
    (included / DATADIR_RULEFILE_NAME).touch()
    excluded = tmp_path / "no"
    excluded.mkdir()

    structural_context = resolve_structural_context(tmp_path)

    assert len(structural_context.datadir_contexts) == 1
    assert structural_context.datadir_contexts[0].datadir == included

# ─── Standalone datadir behaviour ─────────────────────────────


def test_standalone_datadir_returns_single_context(tmp_path):
    """Startdir with .rules is treated as single datadir."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    structural_context = resolve_structural_context(tmp_path)

    assert len(structural_context.datadir_contexts) == 1
    assert structural_context.datadir_contexts[0].datadir == tmp_path


def test_standalone_datadir_is_not_repo_root(tmp_path):
    """If startdir is datadir, is_repo_root is False."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    structural_context = resolve_structural_context(tmp_path)

    assert structural_context.startdir_context.is_repo_root is False


def test_datadir_in_repo_config_rootdir_is_parent(tmp_path):
    """Datadir without .mklistsrc has config_rootdir == startdir.parent."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    structural_context = resolve_structural_context(tmp_path)

    assert structural_context.startdir_context.config_rootdir == tmp_path.parent


def test_selfcontained_datadir_config_rootdir_is_startdir(tmp_path):
    """Self-contained datadir (with .mklistsrc) has config_rootdir == startdir."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()
    (tmp_path / DATADIR_CONFIGFILE_NAME).touch()

    structural_context = resolve_structural_context(tmp_path)

    assert structural_context.startdir_context.config_rootdir == tmp_path


@pytest.mark.parametrize(
    "has_configfile",
    [False, True],
)
def test_standalone_datadir_configfile_detection(tmp_path, has_configfile):
    """Presence (or not) of .mklistsrc is correctly recorded in context."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    if has_configfile:
        (tmp_path / DATADIR_CONFIGFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    expected = tmp_path / DATADIR_CONFIGFILE_NAME if has_configfile else None
    assert result.datadir_contexts[0].datadir_configfile_found == expected


def test_standalone_datadir_rulefile_path(tmp_path):
    """If startdir is datadir, datadir_rulefile points to .rules file."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert result.datadir_contexts[0].datadir_rulefile == (
        tmp_path / DATADIR_RULEFILE_NAME
    )
