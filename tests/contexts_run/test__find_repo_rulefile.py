"""Tests $MKLMKL/contexts_run.py"""

from mklists.structure.contexts_run import _find_repo_rulefile
from mklists.structure.markers import REPO_RULEFILE_NAME


def test_find_repo_rulefile(tmp_path):
    """Finds mklists.rules file, returns absolute path."""
    expected_path = tmp_path / REPO_RULEFILE_NAME
    expected_path.touch()

    resulting_path = _find_repo_rulefile(tmp_path)
    assert resulting_path == expected_path


def test_find_repo_rulefile_none(tmp_path):
    """Finds no mklists.rules file, returns None."""
    assert _find_repo_rulefile(tmp_path) is None
