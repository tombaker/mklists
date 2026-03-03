"""Resolve structural context for a single datadir."""

from operator import attrgetter
from pathlib import Path
from mklists.errors import StructureError
from mklists.rules.load import load_rules_for_datadir
from mklists.structure.markers import (
    DATADIR_CONFIGFILE_NAME,
    DATADIR_RULEFILE_NAME,
    REPO_CONFIGFILE_NAME,
    REPO_RULEFILE_NAME,
)
from mklists.structure.model import (
    DatadirStructuralContext, 
    StartdirStructuralContext, 
    StructuralContext,
)


def resolve_structural_context(startdir: Path | str) -> StructuralContext:
    """Derive structural context from filesystem layout.

    Args:
        startdir: Path of starting directory: CWD path or override path from CLI option.

    Returns:
        Structural context derived from filesystem layout.
    """
    startdir = Path(startdir).resolve()

    # 1. Determine startdir context.

    startdir_context = _resolve_startdir_context(startdir)

    # 2. Determine effective config_rootdir (for resolving relative paths).
    config_rootdir = _determine_config_rootdir(
        startdir=startdir_context.startdir,
        repo_configfile_found=startdir_context.repo_configfile_found,
        repo_rulefile_found=startdir_context.repo_rulefile_found,
    )

    # 3. Discover Datadirs
    datadirs = _find_datadirs(config_rootdir)

    if not datadirs:
        raise StructureError("No datadirs found under config root directory.")

    # 4. Resolve each DatadirStructuralContext and build list.
    datadir_contexts: list[DatadirStructuralContext] = []

    for datadir in datadirs:
        context = _resolve_datadir_context(
            datadir=datadir,
            repo_configfile_found=repo_configfile_found,
            repo_rulefile_found=repo_rulefile_found,
        )
        datadir_contexts.append(context)

    # 5. Emit fully resolved StructuralContext
    return StructuralContext(
        startdir_context=startdir_context,
        datadir_contexts=datadir_contexts,
    )


def _find_datadirs(config_rootdir: Path | str) -> list[Path]:
    """List paths of data directories under config root directory.

    Args:

        config_rootdir: Path of config root directory.

    Yields:
        Paths of directories directly under repository root that hold a `.rules` file.
    """
    datadirs: list[Path] = []

    for entry in config_rootdir.iterdir():
        is_directory = entry.is_dir()
        has_rules_file = (entry / ".rules").is_file()

        if is_directory and has_rules_file:
            datadirs.append(entry)

    return sorted(datadirs, key=attrgetter("name"))


def _find_repo_configfile(dirpath: Path) -> Path | None:
    """Return repo config file if present in dirpath."""
    candidate = dirpath / REPO_CONFIGFILE_NAME
    return candidate if candidate.is_file() else None


def _find_repo_rulefile(dirpath: Path) -> Path | None:
    """Return repo rulefile if present in dirpath."""
    candidate = dirpath / REPO_RULEFILE_NAME
    return candidate if candidate.is_file() else None


def _determine_config_rootdir(
    *,
    startdir: Path,
    repo_configfile_found: Path | None,
    repo_rulefile_found: Path | None,
) -> Path:
    """Determine directory that serves as configuration root for the run.

    Args:
        startdir: Path of starting directory.
        repo_configfile_found: Path of mklists.yaml (if it exists).
        repo_rulefile_found: Path of mklists.rules (if it exists).

    Returns:
        Path to directory that anchors config and execution for this run.

    Raises:
        StructureError if structure is invalid.

    Note:
        Effective config root directory is either:
        - a repository root (contains `mklists.yaml` or `mklists.rules`), or
        - a self-contained datadir (contains `.mklistsrc`)

        Config root directory may be used as:
        - base for backup directories
        - base for linkify directories
        

        if repo_configfile_found    -> is_repo_rootdir is_config_rootdir
        if repo_rulefile_found      -> is_repo_rootdir is_config_rootdir
        if config_configfile_found  -> is_datadir      is_config_rootdir is_selfcontained
        if config_rulefile_found    -> is_datadir
    """
    datadir_rulefile = startdir / DATADIR_RULEFILE_NAME
    is_datadir = datadir_rulefile.is_file()
    is_repo_root = repo_configfile_found is not None or repo_rulefile_found is not None

    # Structural invariant: cannot be both
    if is_datadir and is_repo_root:
        raise StructureError("Directory cannot be both repository root and datadir.")

    # Repo mode
    if is_repo_root:
        return startdir

    # Single-datadir convenience mode
    if is_datadir:
        return startdir

    raise StructureError("Directory is neither repository root nor datadir.")


def _resolve_datadir_context(
    *,
    datadir: Path,
    repo_configfile_found: Path | None,
    repo_rulefile_found: Path | None,
) -> DatadirStructuralContext:
    """Resolve execution context for a single datadir.

    Args:
        datadir:
        repo_configfile_found:
        repo_rulefile_found:

    Returns:
        DatadirStructuralContext object holding execution context for a single datadir.
    """

    datadir = Path(datadir)
    datadir_rulefile = datadir / DATADIR_RULEFILE_NAME
    datadir_configfile_found = datadir / DATADIR_CONFIGFILE_NAME
    is_self_contained = (datadir / DATADIR_CONFIGFILE_NAME).is_file()

    if is_self_contained:
        configfile_used = datadir_configfile_found
    else:
        configfile_used = repo_configfile_found  # As passed in; this could be None.

    # Config rootdir is used for resolving relative paths in the config universe.
    # It is the directory that contains config file actually used.
    # When no config file exists, config rootdir defaults to Datadir.
    if configfile_used is None:
        config_rootdir = datadir
    else:
        config_rootdir = configfile_used.parent

    # If Datadir is self-contained (config root is itself), ignore repo-level rules.
    if (not is_self_contained) and repo_rulefile_found is not None:
        rulefiles_used = [repo_rulefile_found, datadir_rulefile]
    else:
        rulefiles_used = [datadir_rulefile]

    # Parse rules
    rules = load_rules_for_datadir(rulefiles_used)

    return DatadirStructuralContext(
        datadir=datadir,
        configfile_used=configfile_used,
        config_rootdir=config_rootdir,
        rulefiles_used=rulefiles_used,
        rules=rules,
    )


def _resolve_startdir_context(startdir: Path) -> StartdirStructuralContext:
    """Resolve structural context of startdir.

    Args:
        startdir: Path of starting directory.

    Returns:
        StartdirStructuralContext instance with resolve structural context of startdir.
    """
    startdir_repo_configfile = startdir / REPO_CONFIGFILE_NAME
    if startdir_repo_configfile.is_file():
        repo_configfile_found = startdir_repo_configfile
    else:
        repo_configfile_found = None

    startdir_repo_rulefile = startdir / REPO_RULEFILE_NAME
    if startdir_repo_rulefile.is_file():
        repo_rulefile_found = startdir_repo_rulefile
    else:
        repo_rulefile_found = None

    startdir_datadir_configfile = startdir / DATADIR_CONFIGFILE_NAME
    if startdir_datadir_configfile.is_file():
        datadir_configfile_found = startdir_datadir_configfile
    else:
        datadir_configfile_found = None

    startdir_datadir_rulefile = startdir / DATADIR_RULEFILE_NAME
    if startdir_datadir_rulefile.is_file():
        datadir_rulefile_found = startdir_datadir_rulefile
    else:
        datadir_rulefile_found = None

    return StartdirStructuralContext(
        startdir=startdir,
        repo_configfile_found=repo_configfile_found,
        repo_rulefile_found=repo_rulefile_found,
    )

