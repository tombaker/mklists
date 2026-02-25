"""Tests $MKLMKL/exec/process_datadirs.py"""

from mklists.exec.process_datadirs import _write_datafiles


def test_write_datafiles_single_file(tmp_path):
    """Writes single files."""
    datadir = tmp_path
    datalines_dict = {
        "a.txt": ["one", "two", "three"],
    }

    _write_datafiles(datadir=datadir, datalines_dict=datalines_dict)

    p = datadir / "a.txt"
    assert p.is_file()
    assert p.read_text() == "one\ntwo\nthree\n"


def test_write_datafiles_multiple_files(tmp_path):
    """Writes multiple files."""
    datalines_dict = {
        "b.txt": ["b1"],
        "a.txt": ["a1", "a2"],
    }

    _write_datafiles(datadir=tmp_path, datalines_dict=datalines_dict)

    assert (tmp_path / "a.txt").read_text() == "a1\na2\n"
    assert (tmp_path / "b.txt").read_text() == "b1\n"


def test_write_datafiles_empty_file(tmp_path):
    """Does not write to file if no datalines to write."""
    datalines_dict = {
        "empty.txt": [],
    }

    _write_datafiles(datadir=tmp_path, datalines_dict=datalines_dict)

    p = tmp_path / "empty.txt"
    assert not p.is_file()


def test_write_datafiles_does_not_touch_hidden_files(tmp_path):
    """Hidden files (such as .rules) are not touched."""
    hidden = tmp_path / ".rules"
    hidden.write_text("rules\n")

    datalines_dict = {
        "a.txt": ["x"],
    }

    _write_datafiles(datadir=tmp_path, datalines_dict=datalines_dict)

    assert hidden.read_text() == "rules\n"
    assert (tmp_path / "a.txt").read_text() == "x\n"


def test_write_datafiles_empty_dict(tmp_path):
    """If datalines_dict is empty, no files are written."""
    _write_datafiles(datadir=tmp_path, datalines_dict={})

    # directory remains unchanged
    assert list(tmp_path.iterdir()) == []
