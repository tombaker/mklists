"""@@@"""

from collections.abc import Iterable
from dataclasses import dataclass
from operator import attrgetter
from pathlib import Path
from .backup_datadir import backup_datadir
from .config import MklistsConfig
from .dispatch import dispatch_datalines_to_targets
from .plan import PassPlan
from .rules import Rule
from .safety import run_safety_checks


def process_datadir(
    *,
    context: DatadirContext,
    passplan: PassPlan,
    mklists_cfg: MklistsConfig,
) -> None:
    """
    Args:
        datadir:
        passdir:
        mklists_cfg:

    Returns:
        None, after safety check, reading data, applying rules, backup, re-writing.
    """
    run_safety_checks(context.datadir_path, mklists_cfg.safety)

    rules = context.rules

    datafiles: list[Path] = list(_find_datafiles(context.datadir_path))
    datalines: list[str] = _read_datafiles(datafiles)
    datalines_dict = dispatch_datalines_to_targets(rules, datalines)

    if passplan.backupdir is not None:
        backup_datadir(
            datadir=context.datadir_path,
            passdir=passplan.backupdir,
            backup_depth=mklists_cfg.backup.backup_depth,
        )

    _delete_datafiles(datafiles=datafiles)
    _write_datafiles(datadir=context.datadir_path, datalines_dict=datalines_dict)


def _delete_datafiles(datafiles: list[Path]) -> None:
    """Delete data files.

    Args:
        datafiles: List of data files.

    Returns:
        None, after deleting files.
    """
    for datafile in datafiles:
        datafile.unlink()


def _find_datafiles(datadir: Path | str) -> Iterable[Path]:
    """Yields names of datafiles in given data directory as Path objects.

    Args:
        datadir: Path of data directory.

    Yields:
        Absolute paths of datafiles.

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
    datadir = Path(datadir)

    entries = [
        entry
        for entry in datadir.iterdir()
        if not entry.name.startswith(".") and entry.is_file()
    ]

    yield from sorted(entries, key=attrgetter("name"))


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
