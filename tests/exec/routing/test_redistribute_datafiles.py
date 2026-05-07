"""Tests $MKLMKL/exec/routing.py

No need to test logging for now:
- Logging behavior is not part of contract.
- No need to ensure something is logged for UX reasons.
- Later: caplog (stdlib logging) or Loguru’s logger.catch() tool.
"""

from pathlib import Path
import pytest
from mklists.exec.routing import redistribute_datafiles


@pytest.fixture
def datadirs(tmp_path: Path) -> list[Path]:
    d1 = tmp_path / "data1"
    d2 = tmp_path / "data2"
    d1.mkdir()
    d2.mkdir()
    return [d1, d2]


def test_file_is_moved(datadirs, tmp_path):
    """If routing is enabled and destination directory exists, move file."""
    src = datadirs[0] / "to_a.txt"
    src.write_text("data")

    dest = tmp_path / "a"
    dest.mkdir()

    redistribute_datafiles(
        datadirs=datadirs,
        routing_dict={"to_a.txt": dest},
    )

    assert not src.exists()
    names = [p.name for p in dest.iterdir()]
    assert len(names) == 1
    assert names[0].endswith(".data1.to_a.txt")


def test_dest_missing_file_not_moved(datadirs, tmp_path):
    """If destination directory is missing, file stays put."""
    src = datadirs[0] / "to_a.txt"
    src.write_text("data")

    dest = tmp_path / "missing_dir"  # not created

    redistribute_datafiles(
        datadirs=datadirs,
        routing_dict={"to_a.txt": dest},
    )

    assert src.exists()


def test_multiple_datadirs(tmp_path):
    """Multiple datadirs are handled independently."""
    d1 = tmp_path / "d1"
    d2 = tmp_path / "d2"
    d1.mkdir()
    d2.mkdir()

    (d1 / "to_a.txt").write_text("one")
    (d2 / "to_a.txt").write_text("two")

    dest = tmp_path / "a"
    dest.mkdir()

    redistribute_datafiles(
        datadirs=[d1, d2],
        routing_dict={"to_a.txt": dest},
    )

    assert not (d1 / "to_a.txt").exists()
    assert not (d2 / "to_a.txt").exists()
    names = [p.name for p in dest.iterdir()]
    assert any(n.endswith(".d1.to_a.txt") for n in names)
    assert any(n.endswith(".d2.to_a.txt") for n in names)


def test_redistribute_datafiles_no_collision(tmp_path: Path):
    """Integration test of _unique_destination_filename via redistribute_datafiles."""
    d1 = tmp_path / "a"
    d2 = tmp_path / "b"
    d1.mkdir()
    d2.mkdir()

    (d1 / "to_a.txt").write_text("one")
    (d2 / "to_a.txt").write_text("two")

    dest = tmp_path / "dest"
    dest.mkdir()

    redistribute_datafiles(
        datadirs=[d1, d2],
        routing_dict={"to_a.txt": dest},
    )

    names = [p.name for p in dest.iterdir()]
    assert len(names) == 2
    assert any(n.endswith(".a.to_a.txt") for n in names)
    assert any(n.endswith(".b.to_a.txt") for n in names)
