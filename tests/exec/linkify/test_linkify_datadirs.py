"""Tests for $MKLMKL/exec/linkify.py"""

from mklists.exec.linkify import linkify_datadirs


def test_linkify_datadirs_flat_creates_md_files(tmp_path):
    """Flat layout: .md files are written directly into linkify_dir."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    (datadir / "notes.txt").write_text("alpha\nbeta\n")

    linkify_dir = tmp_path / "linkified"
    linkify_datadirs(datadirs=[datadir], linkify_dir=linkify_dir)

    assert (linkify_dir / "notes.txt.md").is_file()


def test_linkify_datadirs_flat_file_naming(tmp_path):
    """Original filename gets .md appended, not substituted."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    (datadir / "todo.txt").write_text("one\ntwo\n")

    linkify_dir = tmp_path / "linkified"
    linkify_datadirs(datadirs=[datadir], linkify_dir=linkify_dir)

    assert (linkify_dir / "todo.txt.md").is_file()
    assert not (linkify_dir / "todo.md").exists()


def test_linkify_datadirs_flat_content_wrapped_in_pre(tmp_path):
    """Output file contains a <pre> block with the original lines."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    (datadir / "notes.txt").write_text("alpha\nbeta\n")

    linkify_dir = tmp_path / "linkified"
    linkify_datadirs(datadirs=[datadir], linkify_dir=linkify_dir)

    content = (linkify_dir / "notes.txt.md").read_text()
    assert "<pre>" in content
    assert "alpha" in content
    assert "beta" in content
    assert "</pre>" in content


def test_linkify_datadirs_flat_urls_linkified(tmp_path):
    """URLs in data files are converted to anchor tags in the .md output."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    (datadir / "links.txt").write_text("see https://example.com today\n")

    linkify_dir = tmp_path / "linkified"
    linkify_datadirs(datadirs=[datadir], linkify_dir=linkify_dir)

    content = (linkify_dir / "links.txt.md").read_text()
    assert '<a href="https://example.com">https://example.com</a>' in content


def test_linkify_datadirs_flat_hidden_files_skipped(tmp_path):
    """Hidden files (e.g. .rules) are not mirrored."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    (datadir / ".rules").write_text("hidden\n")
    (datadir / "visible.txt").write_text("line\n")

    linkify_dir = tmp_path / "linkified"
    linkify_datadirs(datadirs=[datadir], linkify_dir=linkify_dir)

    assert not (linkify_dir / ".rules.md").exists()
    assert (linkify_dir / "visible.txt.md").is_file()


# ---------------------------------------------------------------------------
# linkify_datadirs — subdir layout (multiple datadirs one level under root)
# ---------------------------------------------------------------------------


def test_linkify_datadirs_subdir_creates_subdirectories(tmp_path):
    """Subdir layout: each datadir maps to a subdirectory of linkify_dir."""
    root = tmp_path / "root"
    root.mkdir()
    (root / "work").mkdir()
    (root / "home").mkdir()
    (root / "work" / "tasks.txt").write_text("task one\n")
    (root / "home" / "chores.txt").write_text("chore one\n")

    linkify_dir = tmp_path / "linkified"
    linkify_datadirs(
        datadirs=[root / "work", root / "home"],
        linkify_dir=linkify_dir,
    )

    assert (linkify_dir / "work" / "tasks.txt.md").is_file()
    assert (linkify_dir / "home" / "chores.txt.md").is_file()


# ---------------------------------------------------------------------------
# linkify_datadirs — stale content is cleared
# ---------------------------------------------------------------------------


def test_linkify_datadirs_clears_stale_content(tmp_path):
    """All existing content under linkify_dir is deleted before writing."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    (datadir / "current.txt").write_text("fresh\n")

    linkify_dir = tmp_path / "linkified"
    linkify_dir.mkdir()
    stale = linkify_dir / "old_subdir"
    stale.mkdir()
    (stale / "stale.txt.md").write_text("stale content\n")

    linkify_datadirs(datadirs=[datadir], linkify_dir=linkify_dir)

    assert not stale.exists()
    assert (linkify_dir / "current.txt.md").is_file()


def test_linkify_datadirs_works_when_linkify_dir_absent(tmp_path):
    """linkify_dir is created if it does not yet exist."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    (datadir / "notes.txt").write_text("line\n")

    linkify_dir = tmp_path / "linkified"
    assert not linkify_dir.exists()

    linkify_datadirs(datadirs=[datadir], linkify_dir=linkify_dir)

    assert linkify_dir.is_dir()
    assert (linkify_dir / "notes.txt.md").is_file()
