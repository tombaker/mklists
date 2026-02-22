"""Tests $MKLSTRUCTURE/contexts_datadir.py"""

from mklists.structure.contexts_datadir import _find_datadir_configfile
from mklists.structure.markers import DATADIR_CONFIGFILE_NAME


def test_find_datadir_configfile(tmp_path):
    """Finds .mklistsrc file, returns absolute path."""
    expected_path = tmp_path / DATADIR_CONFIGFILE_NAME
    expected_path.touch()

    resulting_path = _find_datadir_configfile(tmp_path)
    assert resulting_path == expected_path


def test_find_datadir_configfile_none(tmp_path):
    """Finds no .mklistsrc file, returns None."""
    assert _find_datadir_configfile(tmp_path) is None
