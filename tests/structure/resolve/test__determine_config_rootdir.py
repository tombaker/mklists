"""Tests $MKLMKL/structure/resolve.py"""

from pathlib import Path
import pytest
from mklists.errors import StructureError

# from mklists.structure.resolve import _determine_config_rootdir
from mklists.structure.markers import DATADIR_RULEFILE_NAME


@pytest.mark.skip
def test_determine_rundir_repo_mode(tmp_path):
    """Sees mklists.yaml (passed as argument): startdir is also config_rootdir."""
    startdir = tmp_path

    resulting_config_rootdir = _determine_config_rootdir(
        startdir=startdir,
        repo_configfile=startdir / "mklists.yaml",
        repo_rulefile=None,
    )

    assert resulting_config_rootdir == startdir


@pytest.mark.skip
def test_determine_rundir_datadir_mode(tmp_path):
    """Sees .rules (by checking filesystem): startdir is also config_rootdir."""
    startdir = tmp_path
    (startdir / DATADIR_RULEFILE_NAME).touch()

    result = _determine_config_rootdir(
        startdir=startdir,
        repo_configfile=None,
        repo_rulefile=None,
    )

    assert result == startdir


@pytest.mark.skip
def test_determine_rundir_both_markers_raises(tmp_path):
    """Sees both mklists.yaml and .rules: raises exception."""
    startdir = tmp_path
    (startdir / DATADIR_RULEFILE_NAME).touch()

    with pytest.raises(StructureError):
        _determine_config_rootdir(
            startdir=startdir,
            repo_configfile=startdir / "mklists.yaml",
            repo_rulefile=None,
        )


@pytest.mark.skip
def test_determine_rundir_neither_raises(tmp_path):
    """Sees neither mklists.yaml nor .rules: raises exception."""
    with pytest.raises(StructureError):
        _determine_config_rootdir(
            startdir=tmp_path,
            repo_configfile=None,
            repo_rulefile=None,
        )
