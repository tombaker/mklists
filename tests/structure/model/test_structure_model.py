"""Structural model objects are immutable by design."""

from pathlib import Path
import pytest
from mklists.structure.model import (
    DatadirStructuralContext,
    StartdirStructuralContext,
    StructuralContext,
)


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
        ),
        StructuralContext(
            startdir_context=StartdirStructuralContext(
                startdir=Path("/tmp"),
                repo_configfile_found=None,
                repo_rulefile_found=None,
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
