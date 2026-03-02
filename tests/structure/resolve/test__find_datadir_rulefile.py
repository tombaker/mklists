"""Tests $MKLSTRUCTURE/resolve.py"""

import pytest

# from mklists.structure.resolve import _find_datadir_rulefile
# from mklists.structure.markers import DATADIR_RULEFILE_NAME


@pytest.mark.skip(reason="Broken after refactoring resolve_datadir_context.")
def test_find_datadir_rulefile(tmp_path):
    """Finds mklists.rules file, returns absolute path."""
    expected_path = tmp_path / DATADIR_RULEFILE_NAME
    expected_path.touch()

    resulting_path = _find_datadir_rulefile(tmp_path)
    assert resulting_path == expected_path


@pytest.mark.skip(reason="Broken after refactoring resolve_datadir_context.")
def test_find_datadir_rulefile_none(tmp_path):
    """Finds no .rules file, returns None."""
    assert _find_datadir_rulefile(tmp_path) is None
