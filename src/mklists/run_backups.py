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

def backup_datadirs(
    *,
    datadirs: Iterable[Path],
    pass_backup_root: Path,
) -> None:
    """Create backup snapshot for one execution pass.

    Args:
        datadirs: Iterable of datadir paths to snapshot.
        pass_backup_root: Directory for this pass (must not exist).

    Raises:
        FileExistsError: If pass_backup_root already exists.
    """
    if pass_backup_root.exists():
        raise FileExistsError(
            f"Pass backup directory already exists: {pass_backup_root}"
        )

    pass_backup_root.mkdir(parents=True)

    for datadir in datadirs:
        target = pass_backup_root / datadir.name
        shutil.copytree(datadir, target)

def run_backups(*, datadir: Path, backupdir: Path) -> Path:
    """Back up ...

    No timestamp.
    No depth.
    No config.
    No rulefiles.

    Args:
        datadir: Data directory.
        backupdir: Backup directory for this pass.
        backup_depth: Number of backup directories to retain.

    Return:
        Path of backup directory for this pass.
    """
    logger.info(f"Backup {backupdir}")
    _prune_backupdirs(
        backupdir=backupdir,
        backup_depth=backup_depth,
    )
    return backupdir


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
    backupdir: Path, user_configfile: Path | None, global_rulefile: Path | None = None
) -> None:
    """Initialize directory for backup of one pass of a mklists run.

    Args:
        backupdir: Backup directory to initialize.
        user_configfile: Path of user config file (or None if none exists).

    Returns:
        None, after creating and initializing the backup root directory.

    Raises:
        FileExistsError: If backup root directory already exists.
    """
    backupdir.mkdir(parents=True, exist_ok=False)

    if user_configfile is not None and user_configfile.is_file():
        shutil.copy2(user_configfile, backupdir)

    if global_rulefile is not None and global_rulefile.is_file():
        shutil.copy2(global_rulefile, backupdir)
