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
    """Exit with error message after blank line found."""
    os.chdir(tmp_path)
    Path("foo").write_text("foo stuff\n\nmore foo stuff\n")
    Path("bar").write_text("bar stuff\n")
    with pytest.raises(SystemExit):
        get_datalines()


def test_exit_if_non_utf8_found(tmp_path):
    """Exit with error message after non-UTF8 material found.
    Todo: find out how to write non-UTF8 to a file."""
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
    """Exit with error message if there is no data to process."""
    os.chdir(tmp_path)
    Path("foo").write_text("")
    Path("bar").write_text("")
    with pytest.raises(SystemExit):
        get_datalines()
