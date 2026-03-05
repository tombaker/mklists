"""Structural model objects are immutable by design."""

from pathlib import Path
import pytest
from mklists.errors import StructureError
from mklists.structure.model import (
    DatadirStructuralContext,
    StartdirStructuralContext,
    StructuralContext,
)


def test_config_rootdir_raises_on_all_none_discovery_fields():
    """Accessing config_rootdir raises StructureError when all discovery fields are None.

    This test does not represent a state that arises from normal filesystem discovery.
    Upstream resolution logic guarantees that at least one of the four discovery fields
    (repo_configfile_found, repo_rulefile_found, datadir_configfile_found,
    datadir_rulefile_found) will be set before config_rootdir is ever accessed.

    The guard in config_rootdir — `raise StructureError("Unreachable structural state.")`
    — exists to make that invariant explicit and to produce a clear error if it is
    ever violated by a future refactor. This test documents that contract: if somehow
    all discovery fields are None, the property raises rather than returning silently
    incorrect results.
    """
    ctx = StartdirStructuralContext(
        startdir=Path("/tmp"),
        repo_configfile_found=None,
        repo_rulefile_found=None,
        datadir_configfile_found=None,
        datadir_rulefile_found=None,
    )

    with pytest.raises(StructureError):
        _ = ctx.config_rootdir


@pytest.mark.parametrize(
    "instance",
    [
        DatadirStructuralContext(
            datadir=Path("/tmp"),
            datadir_configfile_found=None,
            datadir_rulefile=Path("/tmp/.rules"),
        ),
        StartdirStructuralContext(
            startdir=Path("/tmp"),
            repo_configfile_found=None,
            repo_rulefile_found=None,
            datadir_configfile_found=None,
            datadir_rulefile_found=Path("/tmp/.rules"),
        ),
        StructuralContext(
            startdir_context=StartdirStructuralContext(
                startdir=Path("/tmp"),
                repo_configfile_found=None,
                repo_rulefile_found=None,
                datadir_configfile_found=None,
                datadir_rulefile_found=Path("/tmp/.rules"),
            ),
            datadir_contexts=[],
        ),
    ],
)
def test_structural_contexts_are_immutable(instance):
    """Structural model objects are immutable by architectural design."""
    with pytest.raises((AttributeError, TypeError)):
        instance.__dict__  # will fail if slots=True

    with pytest.raises((AttributeError, TypeError)):
        setattr(instance, "new_field", 123)
