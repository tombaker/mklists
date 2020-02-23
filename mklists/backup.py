"""Functions related to backups."""

import shutil
from pathlib import Path
from .apply import _ls_visiblefile_paths, _find_rootdir_path
from .config import BACKUPDIR_NAME, TIMESTAMP_STR
from .exceptions import MklistsError


def move_datafiles_to_backupdir(
    datadir=None, backupdir_name=BACKUPDIR_NAME, now=TIMESTAMP_STR
):
    """Move visible files in given data directory to named backup directory."""
    # backup_depth, rootdir_path
    if not datadir:
        datadir = Path.cwd()
    backupsub_path = _form_backupsub_pathname(
        datadir=datadir, backupdir_name=backupdir_name, now=now
    )
    backupsub_path.mkdir(parents=True, exist_ok=True)
    for visible_file in _ls_visiblefile_paths(datadir):
        shutil.move(str(visible_file), backupsub_path)


def _form_backupsub_pathname(
    datadir=None, backupdir_name=BACKUPDIR_NAME, now=TIMESTAMP_STR
):
    """Return backups Path named for cwd."""
    rootdir = _find_rootdir_path()
    if not datadir:
        datadir = Path.cwd()
    sub_name = str(Path(datadir).relative_to(rootdir)).strip("/").replace("/", "_")
    backupsub_path = Path(rootdir) / backupdir_name / sub_name / now
    return backupsub_path


def delete_older_backupdirs(
    depth=None, rootdir_path=None, backupdir_name=BACKUPDIR_NAME
):
    """Delete all but specified number of backups of current working directory."""
    if not rootdir_path:
        rootdir_path = _find_rootdir_path()
    if not depth:
        depth = 0
    try:
        depth = abs(int(depth))
    except (ValueError, TypeError):
        raise MklistsError(f"Bad value for depth: {depth}")
    backup_path = Path(rootdir_path) / backupdir_name
    subdirs = []
    for subdir in sorted(Path(backup_path).glob("*")):
        subdirs.append(subdir)
        subsubdirs = []
        for subsubdir in sorted(Path(subdir).glob("*")):
            subsubdirs.insert(0, subsubdir)
        while len(subsubdirs) > depth:
            directory_to_be_deleted = subsubdirs.pop()
            shutil.rmtree(directory_to_be_deleted)
    for subdir in subdirs:
        try:
            subdir.rmdir()
        except OSError:
            pass
