"""Tests $MKLMKL/contexts_run.py"""

from pathlib import Path
import pytest
from mklists.contexts_run import _determine_rundir
from mklists.errors import StructureError
from mklists.structure import DATADIR_RULEFILE_NAME


def test_determine_rundir_repo_mode(tmp_path):
    """Sees startdir/mklists.yaml (from function call): startdir is also rundir."""
    startdir = tmp_path

    resulting_rundir = _determine_rundir(
        startdir=startdir,
        repo_configfile=startdir / "mklists.yaml",
        repo_rulefile=None,
    )

    assert resulting_rundir == startdir


def test_determine_rundir_datadir_mode(tmp_path):
    """Sees startdir/.rules (by checking filesystem): startdir is also rundir."""
    startdir = tmp_path
    (startdir / DATADIR_RULEFILE_NAME).touch()

    result = _determine_rundir(
        startdir=startdir,
        repo_configfile=None,
        repo_rulefile=None,
    )

    assert result == startdir


def test_determine_rundir_both_markers_raises(tmp_path):
    """Sees both mklists.yaml and .rules: raises exception."""
    startdir = tmp_path
    (startdir / DATADIR_RULEFILE_NAME).touch()

    with pytest.raises(StructureError):
        _determine_rundir(
            startdir=startdir,
            repo_configfile=startdir / "mklists.yaml",
            repo_rulefile=None,
        )


def test_determine_rundir_neither_raises(tmp_path):
    """Sees neither mklists.yaml nor .rules: raises exception."""
    with pytest.raises(StructureError):
        _determine_rundir(
            startdir=tmp_path,
            repo_configfile=None,
            repo_rulefile=None,
        )
