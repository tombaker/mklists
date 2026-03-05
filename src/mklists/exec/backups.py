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
    snapshot_dir: Path,
) -> None:
    """Copy datadirs into already-initialized snapshot directory.

    Args:
        datadirs: Datadirs to snapshot.
        snapshot_dir: Directory for snapshots of datadirs.

    Raises:
        FileExistsError: If snapshot_dir already exists.
    """
    if not snapshot_dir.exists() or not snapshot_dir.is_dir():
        raise FileNotFoundError(
            f"Backup snapshot directory does not exist: {snapshot_dir}"
        )

    logger.info(f"Backup {snapshot_dir}")

    for datadir in datadirs:
        target = snapshot_dir / datadir.name
        shutil.copytree(src=datadir, dst=target)


def init_snapshot_dir(
    snapshot_dir: Path,
    snapshot_repofiles_to_copy: list[Path],
) -> None:
    """Initialize directory for backup of one pass of a mklists run.

    Args:
        snapshot_dir: Backup directory to initialize.
        snapshot_repofiles_to_copy: List of repo-level config files to back up.

    Returns:
        None, after creating and initializing the backup root directory.

    Raises:
        FileExistsError: If backup root directory already exists.
    """
    snapshot_dir.mkdir(parents=True, exist_ok=False)

    for repofile_to_snapshot in snapshot_repofiles_to_copy:
        shutil.copy2(src=repofile_to_snapshot, dst=snapshot_dir)


def prune_backupdirs(backup_rootdir: Path, backup_depth: int) -> None:
    """Delete oldest backup directories exceeding backup depth.

    Args:
        backup_rootdir: Path of backups tree.
        backup_depth: Number of backup directories to retain for given datadir.

    Returns:
        None, after deleting directories.
    """
    run_backupdirs = sorted(p for p in backup_rootdir.iterdir() if p.is_dir())

    excess = len(run_backupdirs) - backup_depth
    if excess <= 0:
        return

    for olddir in run_backupdirs[:excess]:
        shutil.rmtree(path=olddir)
