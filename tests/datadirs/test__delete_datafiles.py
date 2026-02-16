"""Tests $MKLMKL/datadirs.py"""

from mklists.datadirs import _delete_datafiles


def test_delete_datafiles(tmp_path):
    """No guards, logging, conditionals: failures surface if invariants violated."""
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("a")
    f2.write_text("b")

    _delete_datafiles([f1, f2])

    assert not f1.exists()
    assert not f2.exists()
