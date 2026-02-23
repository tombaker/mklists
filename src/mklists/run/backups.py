"""Backup of files before destructive re-write of data directory.

Run layer:
- manipulates containers of backups, not the data inside them
- naming
- inheritance of config
- pruning logic
"""

import shutil
from pathlib import Path
from typing import Iterable
from loguru import logger


def backup_datadirs(
    *,
    datadirs: Iterable[Path],
    backup_snapshot_dir: Path,
) -> None:
    """Create backup snapshot of all Datadirs to be processed in one execution pass.

    Args:
        datadirs: Iterable of Datadirs to snapshot.
        backup_snapshot_dir: Root directory for snapshots of Datadirs.

    Raises:
        FileExistsError: If backup_snapshot_dir already exists.
    """
    if backup_snapshot_dir.exists():
        raise FileExistsError(
            f"Pass backup directory already exists: {backup_snapshot_dir}"
        )

    backup_snapshot_dir.mkdir(parents=True)
    logger.info(f"Backup {backup_snapshot_dir}")

    for datadir in datadirs:
        target = backup_snapshot_dir / datadir.name
        shutil.copytree(src=datadir, dst=target)


def init_backup_snapshot_dir(
    backup_snapshot_dir: Path,
    repo_configfile: Path | None,
    repo_rulefile: Path | None = None,
) -> None:
    """Initialize directory for backup of one pass of a mklists run.

    Args:
        backup_snapshot_dir: Backup directory to initialize.
        repo_configfile: Path of repo-level config file (or None if none exists).
        repo_rulefile: Path of repo-level rule file (or None if none exists).

    Returns:
        None, after creating and initializing the backup root directory.

    Raises:
        FileExistsError: If backup root directory already exists.
    """
    backup_snapshot_dir.mkdir(parents=True, exist_ok=False)

    if repo_configfile is not None and repo_configfile.is_file():
        shutil.copy2(src=repo_configfile, dst=backup_snapshot_dir)

    if repo_rulefile is not None and repo_rulefile.is_file():
        shutil.copy2(src=repo_rulefile, dst=backup_snapshot_dir)


def prune_backupdirs(backups_rootdir: Path, backup_depth: int) -> None:
    """Delete oldest backup directories exceeding backup_depth.

    Args:
        backups_rootdir: Path of backups tree.
        backup_depth: Number of backup directories to retain for given datadir.

    Returns:
        None, after deleting directories.
    """
    run_backupdirs = sorted(p for p in backups_rootdir.iterdir() if p.is_dir())

    excess = len(run_backupdirs) - backup_depth
    if excess <= 0:
        return

    for olddir in run_backupdirs[:excess]:
        shutil.rmtree(path=olddir)
