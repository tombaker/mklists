"""Write minimal rule files."""

import os
from pathlib import Path
from mklists.config import (
    DATADIR_NAME,
    DATADIR_RULEFILE_MINIMAL_CONTENTS,
    DATADIR_RULEFILE_NAME,
    ROOTDIR_RULEFILE_CONTENTS,
    ROOTDIR_RULEFILE_NAME,
    write_minimal_rulefiles,
)
from mklists.exceptions import ConfigWarning


def test_import_warning():
    """ConfigWarning is a subclass of Warning (and is being properly imported)."""
    assert issubclass(ConfigWarning, Warning)


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


def test_exit_if_rootdir_already_has_rulefile(tmp_path, recwarn):
    """Warns (but does not exit) if rule files exist in root and data directories."""
    os.chdir(tmp_path)
    Path(ROOTDIR_RULEFILE_NAME).write_text("some rootdir rules")
    datadir = Path(DATADIR_NAME)
    datadir.mkdir()
    datadir_rules = Path(DATADIR_NAME) / DATADIR_RULEFILE_NAME
    datadir_rules.write_text("some datadir rules")
    write_minimal_rulefiles()
    assert len(recwarn) == 2
    w = recwarn.pop()
    assert w.category == ConfigWarning
    x = recwarn.pop()
    assert x.category == ConfigWarning
