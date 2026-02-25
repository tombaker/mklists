"""Tests $MKLRUN/process_datadirs"""

from mklists.run.process_datadirs import _find_datafiles


def test_find_datafiles_basic(tmp_path):
    """Visible files in sort order."""
    (tmp_path / "b.txt").write_text("b\n")
    (tmp_path / "a.txt").write_text("a\n")

    files = list(_find_datafiles(tmp_path))

    assert [p.name for p in files] == ["a.txt", "b.txt"]


def test_find_datafiles_excludes_dotfiles(tmp_path):
    """Does not yield dot files."""
    (tmp_path / ".rules").write_text("x\n")
    (tmp_path / "visible.txt").write_text("y\n")

    files = list(_find_datafiles(tmp_path))

    assert [p.name for p in files] == ["visible.txt"]


def test_find_datafiles_yields_files_only_and_excludes_directories(tmp_path):
    """Yields only file paths even if subdirectories are present."""
    (tmp_path / "file.txt").write_text("x\n")
    (tmp_path / "subdir").mkdir()

    files = list(_find_datafiles(tmp_path))

    assert [p.name for p in files] == ["file.txt"]
