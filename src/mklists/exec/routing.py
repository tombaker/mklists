"""About redistributing files among datadirs according to a routing map."""

import shutil
from datetime import UTC, datetime
from pathlib import Path

from mklists.logging import logger


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
                logger.info(
                    f"Dispatch {filename}: dest {dest_dir} not found (drive unmounted?)"
                )
                continue

            destination = _unique_destination_filename(
                datadir=datadir,
                filename=filename,
                dest_dir=dest_dir,
            )

            shutil.move(source, destination)
            logger.info(f"Dispatched {source} to {destination}")


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
        Absolute pathname of target file in destination directory,
        always prefixed with a UTC timestamp so that successive dispatches
        to the same destination accumulate rather than overwrite.
    """
    stem = datadir.name
    src = Path(filename)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")
    return dest_dir / f"{ts}.{stem}.{src.name}"
