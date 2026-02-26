"""Tests $MKLSTRUCTURE/resolve.py"""

import pytest
# from mklists.structure.resolve import _find_datadir_configfile
# from mklists.structure.markers import DATADIR_CONFIGFILE_NAME


@pytest.mark.skip(reason="Broken after refactoring resolve_datadir_context.")
def test_find_datadir_configfile(tmp_path):
    """Finds .mklistsrc file, returns absolute path."""
    expected_path = tmp_path / DATADIR_CONFIGFILE_NAME
    expected_path.touch()

    resulting_path = _find_datadir_configfile(tmp_path)
    assert resulting_path == expected_path


@pytest.mark.skip(reason="Broken after refactoring resolve_datadir_context.")
def test_find_datadir_configfile_none(tmp_path):
    """Finds no .mklistsrc file, returns None."""
    assert _find_datadir_configfile(tmp_path) is None
