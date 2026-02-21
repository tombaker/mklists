"""Tests $MKLMKL/process_datadirs.py """

from mklists.process_datadirs import _read_datafiles


def test_read_datafiles_single_file(tmp_path):
    """Reads multiple lines from single file."""
    datafile = tmp_path / "data.txt"
    datafile.write_text("a\nb\nc\n", encoding="utf-8")

    lines = _read_datafiles([datafile])

    assert lines == ["a", "b", "c"]


def test_read_datafiles_multiple_files(tmp_path):
    """Creates one flat list of lines from multiple files."""
    f1 = tmp_path / "f1.txt"
    f2 = tmp_path / "f2.txt"

    f1.write_text("a\nb\n", encoding="utf-8")
    f2.write_text("c\nd\n", encoding="utf-8")

    lines = _read_datafiles([f1, f2])

    assert lines == ["a", "b", "c", "d"]


def test_read_datafiles_no_trailing_newline(tmp_path):
    """Reads a datafile with no trailing newline."""
    datafile = tmp_path / "data.txt"
    datafile.write_text("a\nb\nc", encoding="utf-8")

    lines = _read_datafiles([datafile])

    assert lines == ["a", "b", "c"]


def test_read_datafiles_empty_input():
    """Empty list of files results in empty list of lines."""
    lines = _read_datafiles([])

    assert not lines  # [] is falsy
