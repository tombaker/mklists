"""Tests $MKLMKL/contexts_datadir.py"""

from mklists.contexts_datadir import _find_datadir_rulefile
from mklists.structure import DATADIR_RULEFILE_NAME


def test_find_datadir_rulefile(tmp_path):
    """Finds mklists.rules file, returns absolute path."""
    expected_path = tmp_path / DATADIR_RULEFILE_NAME
    expected_path.touch()

    resulting_path = _find_datadir_rulefile(tmp_path)
    assert resulting_path == expected_path


def test_find_datadir_rulefile_none(tmp_path):
    """Finds no .rules file, returns None."""
    assert _find_datadir_rulefile(tmp_path) is None
