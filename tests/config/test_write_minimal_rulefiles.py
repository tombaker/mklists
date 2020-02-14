"""Write minimal rule files."""

import os
from pathlib import Path
from mklists.config import (
    DATADIR_NAME,
    DATADIR_RULEFILE_MINIMAL_CONTENTS,
    DATADIR_RULEFILE_NAME,
    ROOTDIR_RULEFILE_CONTENTS,
    ROOTDIR_RULEFILE_NAME,
)
from mklists.config import write_minimal_rulefiles


def test_init_write_minimal_rulefiles(tmp_path):
    """Write global rulefile in root, minimal rulefile in data directory."""
    os.chdir(tmp_path)
    root_rules = Path(ROOTDIR_RULEFILE_NAME)
    root_rules_contents = ROOTDIR_RULEFILE_CONTENTS
    datadir_rules = Path(DATADIR_NAME) / DATADIR_RULEFILE_NAME
    datadir_rules_contents = DATADIR_RULEFILE_MINIMAL_CONTENTS
    write_minimal_rulefiles()
    assert Path(root_rules).read_text() == root_rules_contents
    assert Path(datadir_rules).read_text() == datadir_rules_contents
