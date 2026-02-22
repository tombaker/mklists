"""Tests $MKLMKL/routing.py

Function has three behaviors:
- Base case: datadir prefix avoids collision
- Timestamp fallback: base name already exists
- Hard failure: even timestamped name exists
"""

from pathlib import Path
import pytest
from mklists.run.routing import _unique_destination_filename


def test_unique_destination_filename_basic(tmp_path: Path):
    """Base case: no collision."""
    datadir = tmp_path / "data_a"
    datadir.mkdir()

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    filename = "to_a.txt"

    dest_path = _unique_destination_filename(
        datadir=datadir,
        filename=filename,
        dest_dir=dest_dir,
    )

    assert dest_path.name == "data_a.to_a.txt"
    assert dest_path.parent == dest_dir
    assert not dest_path.exists()


def test_unique_destination_filename_with_timestamp(tmp_path: Path):
    """If base name exists, add timestamp."""
    datadir = tmp_path / "data_a"
    datadir.mkdir()

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    filename = "to_a.txt"

    # Create the base collision file
    base = dest_dir / "data_a.to_a.txt"
    base.write_text("existing")

    dest_path = _unique_destination_filename(
        datadir=datadir,
        filename=filename,
        dest_dir=dest_dir,
    )

    assert dest_path.parent == dest_dir
    assert dest_path.name.startswith("data_a.to_a.")
    assert dest_path.name.endswith(".txt")
    assert dest_path != base
    assert not dest_path.exists()


def test_unique_destination_filename_collision_raises(tmp_path, monkeypatch):
    """Unresolvable collision raises RunTimeError (but should never happen).

    - Because routing.py does `from datetime import datetime, UTC`,
      must patch `mklists.routing.datetime`, not `datetime.datetime`.
    - Controls time deterministically (no reliance on wall-clock timing).
    - No fragile string equality checks beyond structure.
    """
    # pylint: disable = consider-using-from-import,import-outside-toplevel
    import mklists.run.routing as routing

    datadir = tmp_path / "data_a"
    datadir.mkdir()

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    filename = "to_a.txt"

    # Base collision
    (dest_dir / "data_a.to_a.txt").write_text("existing")

    # Fixed timestamp that is forced
    fixed_ts = "20260207T143512123456"
    timestamped = dest_dir / f"data_a.to_a.{fixed_ts}.txt"
    timestamped.write_text("existing")

    # Fake datetime class
    # pylint: disable = missing-class-docstring,missing-function-docstring
    # pylint: disable = too-few-public-methods,protected-access
    class FixedDateTime:
        @staticmethod
        def now(tz):
            from datetime import datetime

            return datetime(2026, 2, 7, 14, 35, 12, 123456, tzinfo=tz)

    # Patch datetime as used in routing.py
    monkeypatch.setattr(routing, "datetime", FixedDateTime)

    with pytest.raises(RuntimeError, match="Unresolvable filename collision"):
        routing._unique_destination_filename(
            datadir=datadir,
            filename=filename,
            dest_dir=dest_dir,
        )
