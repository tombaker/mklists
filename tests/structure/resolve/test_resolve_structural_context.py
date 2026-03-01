"""Tests $MKLMKL/structure/resolve.py"""

import pytest
from mklists.structure import resolve
from mklists.structure.model import DatadirStructuralContext, StructuralContext
from mklists.errors import StructureError


def test_resolve_structural_context_no_datadirs_raises(tmp_path):
    """If no datadirs found, raises exception."""
    (tmp_path / "mklists.yaml").touch()

    with pytest.raises(StructureError):
        resolve.resolve_structural_context(tmp_path)
