"""Writes YAML configuration file, 'mklists.yml', to repo root directory."""

import os
from pathlib import Path
from mklists.config import (
    DATADIR_NAME,
    DATADIR_DATAFILE_NAME,
    DATADIR_DATAFILE_CONTENTS,
)
from mklists.config import write_starter_datafile


def test_write_starter_datafile(tmp_path):
    """Write lists/README.txt."""
    os.chdir(tmp_path)
    write_starter_datafile(datadir_name=DATADIR_NAME)
    configfile = Path(tmp_path) / DATADIR_NAME / DATADIR_DATAFILE_NAME
    assert configfile.read_text() == DATADIR_DATAFILE_CONTENTS
