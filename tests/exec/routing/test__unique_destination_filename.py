"""Tests $MKLMKL/exec/routing.py"""

import re
from pathlib import Path
from mklists.exec.routing import _unique_destination_filename


def test_unique_destination_filename(tmp_path: Path):
    """Result is always timestamped: {ts}.{datadir}.{filename}."""
    datadir = tmp_path / "data_a"
    datadir.mkdir()

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    dest_path = _unique_destination_filename(
        datadir=datadir,
        filename="to_a.txt",
        dest_dir=dest_dir,
    )

    assert dest_path.parent == dest_dir
    assert re.match(r"^\d{8}T\d{12}\.data_a\.to_a\.txt$", dest_path.name)
    assert not dest_path.exists()
