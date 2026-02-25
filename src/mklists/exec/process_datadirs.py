"""Process Datadirs."""

from operator import attrgetter
from pathlib import Path
from mklists.config import ConfigContext
from mklists.structure.model import DatadirContext
from mklists.exec.process_datalines import dispatch_datalines_to_targets
from mklists.exec.safety import run_safety_checks


def process_datadir(
    *,
    datadir_ctx: DatadirContext,
    mklists_cfg: ConfigContext,
) -> None:
    """
    Args:
        datadir:
        mklists_cfg:

    Returns:
        None, after safety check, reading data, applying rules, backup, re-writing.
    """
    run_safety_checks(datadir_ctx.datadir, mklists_cfg.safety)

    rules = datadir_ctx.rules

    datafiles: list[Path] = list(_find_datafiles(datadir_ctx.datadir))
    datalines: list[str] = _read_datafiles(datafiles)
    datalines_dict = dispatch_datalines_to_targets(rules, datalines)
    _delete_datafiles(datafiles=datafiles)
    _write_datafiles(datadir=datadir_ctx.datadir, datalines_dict=datalines_dict)


def _delete_datafiles(datafiles: list[Path]) -> None:
    """Delete data files.

    Args:
        datafiles: List of data files.

    Returns:
        None, after deleting files.
    """
    for datafile in datafiles:
        datafile.unlink()


def _find_datafiles(datadir: Path) -> list[Path]:
    """Yields names of datafiles in given data directory as Path objects.

    Args:
        datadir: Path of data directory.

    Yields:
        List of datafiles (absolute pathnames).

    Note:
        By definition, a valid "data directory" in mklists:
        - Contains regular files with text only and with no blank lines.
        - Contains the "hidden" file `.rules` (and optionally `mklists-local`).
        - Contains no directories or symlinks.

        This function:
        - Assumes a data directory that has been validated.
        - Yields pathnames of all visible regular files.
        - Yields files in sorted order.
        - Does not recurse into subdirectories.
    """
    datafiles: list[Path] = []

    for entry in datadir.iterdir():
        is_visible = not entry.name.startswith(".")
        is_file = entry.is_file()

        if is_visible and is_file:
            datafiles.append(entry)

    return sorted(datafiles, key=attrgetter("name"))


def _read_datafiles(datafiles: list[Path]) -> list[str]:
    """Read datafiles and build list of their lines.

    Args:
        datafiles: List of datafiles.

    Return:
        Flat list of datalines from all datafiles.
    """
    datalines: list[str] = []

    for datafile in datafiles:
        with datafile.open(encoding="utf-8") as f:
            datalines.extend(line.rstrip("\n") for line in f)

    return datalines


def _write_datafiles(
    *,
    datadir: Path,
    datalines_dict: dict[str, list[str]],
) -> None:
    """Writes datafiles into datadir based on datalines_dict.

    Args:
        datadir: Path of data directory.
        datalines_dict: Mapping of filenames to lists of datalines.

    Returns:
        None, after writing files to datadir.

    Note:
        - Files are written only if there is at least one dataline.
        - Each dataline is written with a trailing newline.
        - Hidden files in datadir are left untouched.

    Assumptions:
        - Datadir exists.
        - Datadir contains no non-hidden files.
        - Keys of datalines_dict are filenames (no path separators).
        - Values are lists of lines WITHOUT trailing newlines.
    """
    for filename in sorted(datalines_dict):
        datalines = datalines_dict[filename]

        # Do not create empty files
        if not datalines:
            continue

        filepath = datadir / filename
        with filepath.open("w", encoding="utf-8") as f:
            for line in datalines:
                f.write(f"{line}\n")
