"""About redistributing files among datadirs according to a routing map."""

from datetime import datetime, UTC
from pathlib import Path
import shutil
from loguru import logger


def redistribute_datafiles(
    datadirs: list[Path],
    routing_dict: dict[str, Path],
) -> None:
    """Move new datafiles with special names to directories outside datadir.

    Args:
        datadirs:
        routing_dict:
        routing_enabled:

    Returns:
        None, after moving files with special names to directories outside datadir.
    """
    for datadir in datadirs:
        for filename, dest_dir in routing_dict.items():
            source = datadir / filename

            if not source.exists():
                continue

            if not dest_dir.exists():
                # Destination directory may be unavailable - eg, USB drive not mounted.
                continue

            destination = _unique_destination_filename(
                datadir=datadir,
                filename=filename,
                dest_dir=dest_dir,
            )

            shutil.move(source, destination)
            logger.info(f"Move {filename} -> {dest_dir}")


def _unique_destination_filename(
    datadir: Path,
    filename: str,
    dest_dir: Path,
) -> Path:
    """
    Args:
        datadir:
        filename:
        dest_dir:

    Returns:
        Absolute pathname of target file in destination directory.
    """
    stem = datadir.name
    src = Path(filename)

    # Base: <datadir>.<original-name>
    candidate = dest_dir / f"{stem}.{src.name}"
    if not candidate.exists():
        return candidate

    # Timestamp fallback (UTC, timezone-aware)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")
    candidate = dest_dir / f"{stem}.{src.stem}.{ts}{src.suffix}"
    if not candidate.exists():
        return candidate

    # This should never happen
    raise RuntimeError(f"Unresolvable filename collision: {candidate}")
