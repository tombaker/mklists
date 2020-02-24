"""Return list of rule file pathnames."""

import os
from pathlib import Path
from mklists.rules import _find_rulefile_chain
from mklists.config import CONFIGFILE_NAME, ROOTDIR_RULEFILE_NAME, DATADIR_RULEFILE_NAME


def test_find_rulefile_chain_typical(tmp_path):
    """Return list of rulefiles from root to (current) working data directory."""
    os.chdir(tmp_path)
    abc = Path(tmp_path) / "a" / "b" / "c"
    abc.mkdir(parents=True, exist_ok=True)
    Path(tmp_path).joinpath(CONFIGFILE_NAME).write_text("config stuff")
    Path(tmp_path).joinpath(ROOTDIR_RULEFILE_NAME).write_text("rule stuff")
    Path(tmp_path).joinpath("a", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    Path(tmp_path).joinpath("a/b", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    Path(tmp_path).joinpath("a/b/c", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    os.chdir(abc)
    expected = [
        Path(tmp_path) / ROOTDIR_RULEFILE_NAME,
        Path(tmp_path) / "a" / DATADIR_RULEFILE_NAME,
        Path(tmp_path) / "a/b" / DATADIR_RULEFILE_NAME,
        Path(tmp_path) / "a/b/c" / DATADIR_RULEFILE_NAME,
    ]
    assert _find_rulefile_chain(datadir=abc) == expected
    assert Path.cwd() == abc


def test_find_rulefile_chain_ends_before_repo_rootdir(tmp_path):
    """Return list of data directory rulefiles only when 'rules.cfg' not reachable)."""
    os.chdir(tmp_path)
    abc = Path(tmp_path) / "a" / "b" / "c"
    abc.mkdir(parents=True, exist_ok=True)
    Path(tmp_path).joinpath(CONFIGFILE_NAME).write_text("config stuff")
    Path(tmp_path).joinpath("a/b", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    Path(tmp_path).joinpath("a/b/c", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    os.chdir(abc)
    expected = [
        Path(tmp_path) / "a/b" / DATADIR_RULEFILE_NAME,
        Path(tmp_path) / "a/b/c" / DATADIR_RULEFILE_NAME,
    ]
    assert _find_rulefile_chain() == expected


def test_find_rulefile_chain_with_specifying_rootdir(tmp_path):
    """Return correct list when starting directory is explicitly specified."""
    os.chdir(tmp_path)
    abc = Path(tmp_path) / "a" / "b" / "c"
    abc.mkdir(parents=True, exist_ok=True)
    Path(tmp_path).joinpath(CONFIGFILE_NAME).write_text("config stuff")
    Path(tmp_path).joinpath(ROOTDIR_RULEFILE_NAME).write_text("rule stuff")
    Path(tmp_path).joinpath("a", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    Path(tmp_path).joinpath("a/b", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    Path(tmp_path).joinpath("a/b/c", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    expected = [
        Path(tmp_path) / ROOTDIR_RULEFILE_NAME,
        Path(tmp_path) / "a" / DATADIR_RULEFILE_NAME,
        Path(tmp_path) / "a/b" / DATADIR_RULEFILE_NAME,
        Path(tmp_path) / "a/b/c" / DATADIR_RULEFILE_NAME,
    ]
    assert DATADIR_RULEFILE_NAME in os.listdir(Path(tmp_path).joinpath("a/b"))
    assert _find_rulefile_chain(datadir=abc) == expected


def test_find_rulefile_chain_empty_list_when_starting_in_non_datadir(tmp_path):
    """Return empty list when starting in a non-data directory."""
    os.chdir(tmp_path)
    abc = Path(tmp_path) / "a" / "b" / "c"
    d = Path.cwd() / "d"
    abc.mkdir(parents=True, exist_ok=True)
    d.mkdir(parents=True, exist_ok=True)
    Path(CONFIGFILE_NAME).write_text("config stuff")
    Path(ROOTDIR_RULEFILE_NAME).write_text("rule stuff")
    Path(tmp_path).joinpath("a", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    Path(tmp_path).joinpath("a/b", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    Path(tmp_path).joinpath("a/b/c", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    os.chdir(d)
    expected = []
    assert _find_rulefile_chain() == expected


def test_find_rulefile_chain_empty_list_when_starting_in_rootdir(tmp_path):
    """Return list with just rules.cfg run from root directory."""
    os.chdir(tmp_path)
    abc = Path(tmp_path).joinpath("a/b/c")
    abc.mkdir(parents=True, exist_ok=True)
    Path(tmp_path).joinpath(CONFIGFILE_NAME).write_text("config stuff")
    Path(tmp_path).joinpath(ROOTDIR_RULEFILE_NAME).write_text("rule stuff")
    Path(tmp_path).joinpath("a", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    Path(tmp_path).joinpath("a/b", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    Path(tmp_path).joinpath("a/b/c", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    os.chdir(tmp_path)
    expected = [Path(tmp_path) / ROOTDIR_RULEFILE_NAME]
    assert _find_rulefile_chain() == expected
