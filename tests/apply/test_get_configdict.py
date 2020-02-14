"""Return config dictionary from reading config file."""

import os
import pytest
from pathlib import Path
from mklists.config import CONFIGFILE_NAME
from mklists.apply import get_configdict

CONFIGFILE_CONTENT = (
    "verbose: True\n"
    "htmlify: True\n"
    "backup_depth: 3\n"
    "invalid_filename_patterns:\n"
    "- \.swp$\n"
    "- \.tmp$\n"
    "- ~$\n"
    "- ^\.\n"
    "\n"
    "# For given file, destination directory to which it should be moved\n"
    "files2dirs:\n"
    "    to_a.txt: a\n"
    "    to_b.txt: b\n"
    "    to_c.txt: /Users/foo/logs\n"
)

CONFIG_PYOBJ = {
    "verbose": True,
    "htmlify": True,
    "backup_depth": 3,
    "invalid_filename_patterns": ["\\.swp$", "\\.tmp$", "~$", "^\\."],
    "files2dirs": {"to_a.txt": "a", "to_b.txt": "b", "to_c.txt": "/Users/foo/logs"},
}


def test_get_configdict(tmp_path):
    """Return dictionary of configuration settings from YAML file."""
    os.chdir(tmp_path)
    Path(CONFIGFILE_NAME).write_text(CONFIGFILE_CONTENT)
    assert get_configdict() == CONFIG_PYOBJ


def test_get_configdict_from_configfile_with_lines_commented_out(tmp_path):
    """Return configuration dictionary even if some lines are commented out."""
    os.chdir(tmp_path)
    configfile_content = "verbose: False\n" "# htmlify: True\n"
    Path(CONFIGFILE_NAME).write_text(configfile_content)
    expected = {"verbose": False}
    assert get_configdict() == expected


def test_exit_if_configfile_not_found(tmp_path):
    """Raise exception if no configuration YAML file is found."""
    os.chdir(tmp_path)
    with pytest.raises(SystemExit):
        get_configdict()


def test_exit_if_configfile_not_found_when_rootdir_explicitly_specified(tmp_path):
    """Raise exception if no config file found when explicitly specifying rootdir."""
    os.chdir(tmp_path)
    cwd = Path.cwd()
    with pytest.raises(SystemExit):
        get_configdict(rootdir_path=cwd)


def test_exit_if_configfile_has_bad_yaml(tmp_path):
    """Raise exception if config file has bad YAML."""
    os.chdir(tmp_path)
    configfile_content = "DELIBE\nRATELY BAD: -: ^^YAML CONTENT^^\n"
    Path(CONFIGFILE_NAME).write_text(configfile_content)
    with pytest.raises(SystemExit):
        get_configdict()
