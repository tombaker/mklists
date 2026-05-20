"""Resolve structural context for a single datadir."""

from operator import attrgetter
from pathlib import Path
from mklists.errors import StructureError
from mklists.structure.markers import (
    DATADIR_CONFIGFILE_NAME,
    DATADIR_RULEFILE_NAME,
    DATATREE_CONFIGFILE_NAME,
    DATATREE_RULEFILE_NAME,
)
from mklists.structure.model import (
    DatadirStructuralContext,
    StartdirStructuralContext,
    StructuralContext,
)


def resolve_structural_context(startdir: Path | str) -> StructuralContext:
    """Derive structural context from filesystem layout.

    Args:
        startdir: Path of starting directory.

    Returns:
        Structural context derived from filesystem layout.

    Note:
        Execution begins in work tree unless CLI-specified.
    """
    startdir = Path(startdir).absolute()

    # 1. Determine startdir context.
    startdir_context = _resolve_startdir_context(startdir=startdir)

    # 2. Discover datadirs
    config_rootdir = startdir_context.config_rootdir
    if startdir_context.is_datatree_root:
        datadirs = _find_datadirs(config_rootdir=config_rootdir)
    else:
        datadirs = [startdir]

    if not datadirs:
        raise StructureError("No datadirs found in work tree.")

    # 3. Build list of datadir structural contexts.
    datadir_contexts: list[DatadirStructuralContext] = []

    for datadir in datadirs:
        datadir_context = _resolve_datadir_context(datadir=datadir)
        datadir_contexts.append(datadir_context)

    # 4. Emit fully resolved StructuralContext.
    return StructuralContext(
        startdir_context=startdir_context,
        datadir_contexts=datadir_contexts,
    )


def _find_datadirs(config_rootdir: Path | str) -> list[Path]:
    """List paths of data directories under config root directory.

    Args:

        config_rootdir: Path of config root directory.

    Yields:
        Paths of directories directly under datatree root that hold a `.rules` file.
    """
    datadirs: list[Path] = []

    for entry in config_rootdir.iterdir():
        is_directory = entry.is_dir()
        has_rules_file = (entry / ".rules").is_file()

        if is_directory and has_rules_file:
            datadirs.append(entry)

    return sorted(datadirs, key=attrgetter("name"))


def _resolve_datadir_context(datadir: Path) -> DatadirStructuralContext:
    """Resolve execution context for a single datadir.

    Args:
        datadir: Path of datadir.

    Returns:
        Execution context object for a single datadir.
    """

    def if_file_exists(path: Path) -> Path | None:
        return path if path.is_file() else None

    # Datadir must have `.rules` file, by definition.
    datadir_rulefile = datadir / DATADIR_RULEFILE_NAME
    datadir_configfile_found = if_file_exists(datadir / DATADIR_CONFIGFILE_NAME)

    return DatadirStructuralContext(
        datadir=datadir,
        datadir_configfile_found=datadir_configfile_found,
        datadir_rulefile=datadir_rulefile,
    )


def _resolve_startdir_context(startdir: Path) -> StartdirStructuralContext:
    """Resolve structural context of startdir.

    Args:
        startdir: Path of starting directory.

    Returns:
        StartdirStructuralContext instance with resolved structural context of startdir.

        Note:
        Config root directory is used to resolve paths for backup and HTML directories.
    """

    def if_file_exists(path: Path) -> Path | None:
        return path if path.is_file() else None

    datatree_configfile_found = if_file_exists(startdir / DATATREE_CONFIGFILE_NAME)
    datatree_rulefile_found = if_file_exists(startdir / DATATREE_RULEFILE_NAME)
    datadir_configfile_found = if_file_exists(startdir / DATADIR_CONFIGFILE_NAME)
    datadir_rulefile_found = if_file_exists(startdir / DATADIR_RULEFILE_NAME)

    is_datatree_root = bool(datatree_configfile_found or datatree_rulefile_found)
    is_datadir = bool(datadir_rulefile_found)

    if is_datadir and is_datatree_root:
        raise StructureError(
            "Starting directory cannot be both datatree root and datadir."
        )

    if not is_datadir and not is_datatree_root:
        raise StructureError("Starting directory must be datatree root or datadir.")

    return StartdirStructuralContext(
        startdir=startdir,
        datatree_configfile_found=datatree_configfile_found,
        datatree_rulefile_found=datatree_rulefile_found,
        datadir_configfile_found=datadir_configfile_found,
        datadir_rulefile_found=datadir_rulefile_found,
    )
