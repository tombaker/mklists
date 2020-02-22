"""Return list of datalines from reading datafiles."""

import os
import pytest
from pathlib import Path
from mklists.apply import get_datalines


def test_get_datalines(tmp_path):
    """Return list of lines aggregated from all data files."""
    os.chdir(tmp_path)
    Path("bar").write_text("bar stuff\nmore bar stuff\n")
    Path("foo").write_text("foo stuff\n")
    expected_result = ["bar stuff\n", "more bar stuff\n", "foo stuff\n"]
    assert get_datalines() == expected_result


def test_exit_if_blank_lines_found(tmp_path):
    """Exits if file with blank line found."""
    os.chdir(tmp_path)
    Path("foo").write_text("foo stuff\n\nmore foo stuff\n")
    Path("bar").write_text("bar stuff\n")
    with pytest.raises(SystemExit):
        get_datalines()


def test_exit_if_non_utf8_found(tmp_path):
    """Exits if file with non-UTF8 contents found."""
    import pickle

    os.chdir(tmp_path)
    Path("foo").write_text("foo stuff\nmore foo stuff\n")
    barfile = Path("bar.pickle")
    some_data = [{"a": "A", "b": 2, "c": 3.0}]
    with open(barfile, "wb") as fout:
        pickle.dump(some_data, fout)
    with pytest.raises(SystemExit):
        get_datalines()


def test_exit_if_no_data_found(tmp_path):
    """Exit if there is no data to process."""
    os.chdir(tmp_path)
    Path("foo").write_text("")
    Path("bar").write_text("")
    with pytest.raises(SystemExit):
        get_datalines()


def test_exit_if_swap_file_found(tmp_path):
    """Exit if swap file (matching bad_filename_patterns) is found."""
    os.chdir(tmp_path)
    patterns = ["\.swp$", "\.tmp$"]
    Path("foo.swp").write_text("some text")
    with pytest.raises(SystemExit):
        get_datalines(bad_filename_patterns=patterns)
