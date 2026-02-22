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
    """Create backup snapshot for one execution pass.

    Args:
        datadirs: Iterable of datadir paths to snapshot.
        backup_snapshot_dir: Directory for backup snapshot.

    Raises:
        FileExistsError: If backup_snapshot_dir already exists.
    """
    if backup_snapshot_dir.exists():
        raise FileExistsError(
            f"Pass backup directory already exists: {backup_snapshot_dir}"
        )

    backup_snapshot_dir.mkdir(parents=True)

    for datadir in datadirs:
        target = backup_snapshot_dir / datadir.name
        shutil.copytree(src=datadir, dst=target)


def run_backups(*, datadir: Path, backup_snapshot_dir: Path) -> Path:
    """Back up ...

    No timestamp.
    No depth.
    No config.
    No rulefiles.

    Args:
        datadir: Data directory.
        backup_snapshot_dir: Backup directory for this pass.
        backup_depth: Number of backup directories to retain.

    Return:
        Path of backup directory for this pass.
    """
    logger.info(f"Backup {backup_snapshot_dir}")
    _prune_backupdirs(
        backup_snapshot_dir=backup_snapshot_dir,
        backup_depth=backup_depth,
    )
    return backup_snapshot_dir


def _prune_backupdirs(backups_rootdir: Path, backup_depth: int) -> None:
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


def _init_backup_snapshot_dir(
    backup_snapshot_dir: Path, user_configfile: Path | None, global_rulefile: Path | None = None
) -> None:
    """Initialize directory for backup of one pass of a mklists run.

    Args:
        backup_snapshot_dir: Backup directory to initialize.
        user_configfile: Path of user config file (or None if none exists).

    Returns:
        None, after creating and initializing the backup root directory.

    Raises:
        FileExistsError: If backup root directory already exists.
    """
    backup_snapshot_dir.mkdir(parents=True, exist_ok=False)

    if user_configfile is not None and user_configfile.is_file():
        shutil.copy2(src=user_configfile, dst=backup_snapshot_dir)

    if global_rulefile is not None and global_rulefile.is_file():
        shutil.copy2(src=global_rulefile, dst=backup_snapshot_dir)
