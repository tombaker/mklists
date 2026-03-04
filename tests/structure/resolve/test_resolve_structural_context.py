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


def test_raises_when_startdir_has_no_markers(tmp_path):
    """Raises if startdir has no repo or datadir markers."""
    with pytest.raises(StructureError):
        resolve_structural_context(tmp_path)


def test_raises_when_startdir_is_both_repo_root_and_datadir(tmp_path):
    """Raises if startdir has both repo markers and .rules."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    with pytest.raises(StructureError):
        resolve_structural_context(tmp_path)


def test_raises_when_startdir_is_both_repo_root_and_datadir_via_rulefile(tmp_path):
    """Raises if startdir has mklists.rules and .rules."""
    (tmp_path / REPO_RULEFILE_NAME).touch()
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


# ─── Return type ──────────────────────────────────────────────────────────────


def test_returns_structural_context_instance(tmp_path):
    """Returns a StructuralContext instance."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    assert isinstance(resolve_structural_context(tmp_path), StructuralContext)


def test_startdir_context_type(tmp_path):
    """startdir_context field is a StartdirStructuralContext."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert isinstance(result.startdir_context, StartdirStructuralContext)


def test_datadir_contexts_type(tmp_path):
    """Each element in datadir_contexts is a DatadirStructuralContext."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    for ctx in result.datadir_contexts:
        assert isinstance(ctx, DatadirStructuralContext)


def test_accepts_string_path(tmp_path):
    """Accepts a str path, not just a Path object."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(str(tmp_path))

    assert isinstance(result, StructuralContext)


# ─── Repo root: startdir has mklists.yaml or mklists.rules ───────────────────


def test_repo_root_via_yaml_one_datadir(tmp_path):
    """Repo root with mklists.yaml and one datadir returns one datadir context."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    d = tmp_path / "data"
    d.mkdir()
    (d / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert len(result.datadir_contexts) == 1
    assert result.datadir_contexts[0].datadir == d


def test_repo_root_via_rules_file_only(tmp_path):
    """Repo root with mklists.rules (no yaml) and one datadir."""
    (tmp_path / REPO_RULEFILE_NAME).touch()
    d = tmp_path / "data"
    d.mkdir()
    (d / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert len(result.datadir_contexts) == 1


def test_repo_root_is_repo_root(tmp_path):
    """Repo root's startdir_context.is_repo_root is True."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    d = tmp_path / "data"
    d.mkdir()
    (d / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert result.startdir_context.is_repo_root is True


def test_repo_root_config_rootdir_is_startdir(tmp_path):
    """Repo root's config_rootdir equals startdir."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    d = tmp_path / "data"
    d.mkdir()
    (d / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert result.startdir_context.config_rootdir == tmp_path


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
    """All datadirs under repo root appear in result."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    for name in ["alpha", "beta"]:
        d = tmp_path / name
        d.mkdir()
        (d / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert len(result.datadir_contexts) == 2


def test_repo_root_datadir_rulefile_path(tmp_path):
    """datadir_rulefile points to the .rules file in the datadir."""
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

    result = resolve_structural_context(tmp_path)

    assert result.datadir_contexts[0].datadir_configfile_found == d / DATADIR_CONFIGFILE_NAME


def test_repo_root_subdirs_without_rules_are_excluded(tmp_path):
    """Subdirectories that lack .rules are not included as datadirs."""
    (tmp_path / REPO_CONFIGFILE_NAME).touch()
    included = tmp_path / "yes"
    included.mkdir()
    (included / DATADIR_RULEFILE_NAME).touch()
    excluded = tmp_path / "no"
    excluded.mkdir()

    result = resolve_structural_context(tmp_path)

    assert len(result.datadir_contexts) == 1
    assert result.datadir_contexts[0].datadir == included


# ─── Standalone datadir: startdir has .rules but no repo markers ──────────────


def test_standalone_datadir_returns_single_context(tmp_path):
    """Startdir with .rules is treated as a single datadir."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert len(result.datadir_contexts) == 1
    assert result.datadir_contexts[0].datadir == tmp_path


def test_standalone_datadir_is_not_repo_root(tmp_path):
    """Startdir datadir's is_repo_root is False."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert result.startdir_context.is_repo_root is False


def test_datadir_in_repo_config_rootdir_is_parent(tmp_path):
    """Datadir without .mklistsrc has config_rootdir == startdir.parent."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert result.startdir_context.config_rootdir == tmp_path.parent


def test_selfcontained_datadir_config_rootdir_is_startdir(tmp_path):
    """Self-contained datadir (with .mklistsrc) has config_rootdir == startdir."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()
    (tmp_path / DATADIR_CONFIGFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert result.startdir_context.config_rootdir == tmp_path


def test_standalone_datadir_no_configfile(tmp_path):
    """Startdir datadir without .mklistsrc has datadir_configfile_found=None."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert result.datadir_contexts[0].datadir_configfile_found is None


def test_standalone_datadir_with_configfile(tmp_path):
    """Startdir datadir with .mklistsrc has datadir_configfile_found set."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()
    (tmp_path / DATADIR_CONFIGFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert result.datadir_contexts[0].datadir_configfile_found == tmp_path / DATADIR_CONFIGFILE_NAME


def test_standalone_datadir_rulefile_path(tmp_path):
    """Startdir datadir's datadir_rulefile points to its .rules file."""
    (tmp_path / DATADIR_RULEFILE_NAME).touch()

    result = resolve_structural_context(tmp_path)

    assert result.datadir_contexts[0].datadir_rulefile == tmp_path / DATADIR_RULEFILE_NAME
