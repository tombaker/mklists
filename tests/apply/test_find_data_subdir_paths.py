"""Return list of directories with .rules files under (but not including) root."""

import os
from pathlib import Path
from mklists.apply import CONFIGFILE_NAME, DATADIR_RULEFILE_NAME, find_data_subdir_paths


def test_data_subdirs_never_includes_rootdir(tmp_path):
    """List data directories (ie, with rulefiles) under (but not including) root."""
    os.chdir(tmp_path)
    abc = Path.cwd() / "a" / "b" / "c"
    abc.mkdir(parents=True, exist_ok=True)
    Path(CONFIGFILE_NAME).write_text("config stuff")
    Path(DATADIR_RULEFILE_NAME).write_text("rule stuff")
    Path(tmp_path).joinpath("a", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    Path(tmp_path).joinpath("a/b", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    Path(tmp_path).joinpath("a/b/c", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    expected = [
        Path(tmp_path) / "a",
        Path(tmp_path) / "a" / "b",
        Path(tmp_path) / "a" / "b" / "c",
    ]
    assert find_data_subdir_paths() == expected


def test_find_data_subdir_paths_even_if_root_is_not_grandparent(tmp_path):
    """List data directories even for directories without root as (grand)parent."""
    os.chdir(tmp_path)
    a = Path.cwd() / "a"
    a.mkdir()
    bc = Path.cwd() / "b" / "c"
    bc.mkdir(parents=True, exist_ok=True)
    Path(CONFIGFILE_NAME).write_text("config stuff")
    Path(DATADIR_RULEFILE_NAME).write_text("rule stuff")
    Path(tmp_path).joinpath("a", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    Path(tmp_path).joinpath("b/c", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    expected = [Path(tmp_path) / "a", Path(tmp_path) / "b" / "c"]
    assert find_data_subdir_paths() == expected


def test_find_data_subdir_paths_ignoring_hidden_directory(tmp_path):
    """List data directories ignoring a "hidden" directory."""
    os.chdir(tmp_path)
    ab = Path.cwd() / "a" / "b"
    ab.mkdir(parents=True, exist_ok=True)
    c = Path.cwd().joinpath("c")
    c.mkdir()
    hidden = Path.cwd().joinpath(".hidden")
    hidden.mkdir()
    Path(CONFIGFILE_NAME).write_text("config stuff")
    Path(DATADIR_RULEFILE_NAME).write_text("rule stuff")
    Path(tmp_path).joinpath("a", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    Path(tmp_path).joinpath("a/b", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    Path(tmp_path).joinpath("c", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    Path(tmp_path).joinpath(".hidden", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    expected = [Path(tmp_path) / "a", Path(tmp_path) / "a" / "b", Path(tmp_path) / "c"]
    assert find_data_subdir_paths() == expected


def test_find_data_subdir_paths_even_if_just_one(tmp_path):
    """List data directories when there is just one."""
    os.chdir(tmp_path)
    a = Path("a")
    a.mkdir()
    Path(CONFIGFILE_NAME).write_text("config stuff")
    Path(DATADIR_RULEFILE_NAME).write_text("rule stuff")
    Path(tmp_path).joinpath("a", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    expected = [Path(tmp_path) / "a"]
    assert find_data_subdir_paths() == expected


def test_find_data_subdir_paths_even_if_no_rulefile(tmp_path):
    """List data directories even when root directory has no rulefile."""
    os.chdir(tmp_path)
    a = Path("a")
    a.mkdir()
    Path(CONFIGFILE_NAME).write_text("config stuff")
    # NOT Path(DATADIR_RULEFILE_NAME).write_text("rule stuff")
    Path(tmp_path).joinpath("a", DATADIR_RULEFILE_NAME).write_text("rule_stuff")
    expected = [Path(tmp_path) / "a"]
    assert find_data_subdir_paths() == expected
