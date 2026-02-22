"""Tests $MKLMKL/contexts_run.py"""

from mklists.structure.contexts_run import _find_repo_configfile
from mklists.structure.markers import REPO_CONFIGFILE_NAME


def test_find_repo_configfile(tmp_path):
    """Finds mklists.yaml file, returns absolute path."""
    expected_path = tmp_path / REPO_CONFIGFILE_NAME
    expected_path.touch()

    resulting_path = _find_repo_configfile(tmp_path)
    assert resulting_path == expected_path


def test_find_repo_configfile_none(tmp_path):
    """Finds no mklists.yaml file, returns None."""
    assert _find_repo_configfile(tmp_path) is None
