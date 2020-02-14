"""Return list of files in cwd (full pathnames), ignoring hidden files."""

import os
from pathlib import Path
from mklists.apply import _get_visiblefile_paths


def test_get_visiblefile_paths_ignoring_directories(tmp_path):
    """Ignores directory 'baz'."""
    os.chdir(tmp_path)
    Path("bar").write_text("bar stuff")
    Path("foo").write_text("foo stuff")
    Path("baz").mkdir()
    print(os.listdir())
    assert _get_visiblefile_paths() == [
        str(Path("bar").resolve()),
        str(Path("foo").resolve()),
    ]
    assert Path.cwd() == Path(tmp_path)


def test_ignore_hidden_dotfiles(tmp_path):
    """Ignores dot file '.bar'."""
    os.chdir(tmp_path)
    Path(".bar").write_text("bar stuff")
    Path("foo").write_text("foo stuff")
    assert _get_visiblefile_paths() == [str(Path("foo").resolve())]
    assert str(Path(tmp_path) / "foo") == str(Path("foo").resolve())


def test_accepts_filenames_with_spaces(tmp_path):
    """Accepts filenames with spaces."""
    os.chdir(tmp_path)
    Path("foo bar").write_text("foo bar stuff")
    Path("baz").write_text("baz stuff")
    assert _get_visiblefile_paths() == [
        str(Path("baz").resolve()),
        str(Path("foo bar").resolve()),
    ]
    assert Path.cwd() == Path(tmp_path)


def test_accepts_filenames_with_umlauts(tmp_path):
    """Accepts filenames with umlauts."""
    os.chdir(tmp_path)
    Path("föö").write_text("foo stuff")
    Path("bär").write_text("bar stuff")
    assert _get_visiblefile_paths() == [
        str(Path("bär").resolve()),
        str(Path("föö").resolve()),
    ]
    assert Path.cwd() == Path(tmp_path)
