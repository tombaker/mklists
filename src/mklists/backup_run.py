"""Backup of files before destructive re-write of data directory.

Run layer:
- manipulates containers of backups, not the data inside them
- naming
- inheritance of config
- pruning logic
"""

import shutil
from pathlib import Path
from loguru import logger


def run_backups(*, datadir: Path, backupdir_path: Path) -> Path:
    """Back up ...

    No timestamp.
    No depth.
    No config.
    No rulefiles.

    Args:
        datadir: Data directory.
        backupdir_path: Backup directory for this pass.
        backup_depth: Number of backup directories to retain.

    Return:
        Path of backup directory for this pass.
    """
    logger.info(f"Backup {backupdir_path}")
    _prune_backupdirs(
        backupdir_path=backupdir_path,
        backup_depth=backup_depth,
    )
    return backupdir_path


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
        shutil.rmtree(olddir)


def _init_passdir(
    backupdir_path: Path, user_configfile: Path | None, global_rulefile: Path | None = None
) -> None:
    """Initialize directory for backup of one pass of a mklists run.

    Args:
        backupdir_path: Backup directory to initialize.
        user_configfile: Path of user config file (or None if none exists).

    Returns:
        None, after creating and initializing the backup root directory.

    Raises:
        FileExistsError: If backup root directory already exists.
    """
    backupdir_path.mkdir(parents=True, exist_ok=False)

    if user_configfile is not None and user_configfile.is_file():
        shutil.copy2(user_configfile, backupdir_path)

    if global_rulefile is not None and global_rulefile.is_file():
        shutil.copy2(global_rulefile, backupdir_path)
