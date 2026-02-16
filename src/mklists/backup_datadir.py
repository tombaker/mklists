"""Backup of a data directory.

Anything that acts on exactly one datadir.
"""

import shutil
from pathlib import Path


def backup_datadir(*, datadir: Path, passdir: Path) -> Path:
    """Copy datadir into existing directory for backups of one execution pass.

    Args:
        datadir: Data directory.
        passdir: Root of backup tree for this execution pass.

    Return:
        Path of copy of data directory under backup root directory.
    """
    pass_backupdir = passdir / datadir.name
    shutil.copytree(datadir, pass_backupdir)

    return pass_backupdir
