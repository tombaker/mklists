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
from mklists.structure.model import DatadirStructuralContext, StructuralContext


def resolve_structural_context(startdir: Path | str) -> StructuralContext:
    """Derive structural context from filesystem layout.

    Args:
        startdir: Starting directory, based on CWD or CLI option.

    Returns:
        Structural context derived from filesystem layout.
    """
    startdir = Path(startdir).resolve()

    # 1. Look for repo-level markers in startdir.
    repo_configfile = _find_repo_configfile(startdir)
    repo_rulefile = _find_repo_rulefile(startdir)

    # 2. Determine effective config_rootdir, whether Repo Root or single Datadir.
    config_rootdir = _determine_config_rootdir(
        startdir=startdir,
        repo_configfile=repo_configfile,
        repo_rulefile=repo_rulefile,
    )

    # 3. Discover Datadirs
    datadirs = _find_datadirs(config_rootdir)

    if not datadirs:
        raise StructureError("No datadirs found under repository root.")

    # 4. Resolve each DatadirStructuralContext and build list.
    datadir_contexts: list[DatadirStructuralContext] = []

    for datadir in datadirs:
        context = resolve_datadir_context(
            datadir=datadir,
            repo_configfile=repo_configfile,
            repo_rulefile=repo_rulefile,
        )
        datadir_contexts.append(context)

    # 5. Emit fully resolved StructuralContext
    return StructuralContext(
        config_rootdir=config_rootdir,
        repo_configfile=repo_configfile,
        repo_rulefile=repo_rulefile,
        datadir_contexts=datadir_contexts,
    )


def _find_datadirs(repodir: Path | str) -> list[Path]:
    """Yields paths of data directories under repository root.

    Args:

        repodir: Root of Mklists repository tree.

    Yields:
        Paths of directories directly under repository root that hold a `.rules` file.
    """
    datadirs: list[Path] = []

    for entry in repodir.iterdir():
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
    repo_configfile: Path | None,
    repo_rulefile: Path | None,
) -> Path:
    """Determine directory that serves as configuration root for the run.

    Args:
        startdir: Path of starting directory.
        repo_configfile: Path of `mklists.yaml` (if it exists).
        repo_rulefile: Path of `mklists.rules` (if it exists).

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
        - base for urlify directories
    """
    datadir_rulefile = startdir / DATADIR_RULEFILE_NAME
    is_datadir = datadir_rulefile.is_file()
    is_repo_root = repo_configfile is not None or repo_rulefile is not None

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
    repo_configfile: Path | None,
    repo_rulefile: Path | None,
) -> DatadirStructuralContext:
    """Resolve execution context for a single datadir.

    Args:
        datadir:
        repo_configfile:
        repo_rulefile:

    Returns:
        DatadirStructuralContext object holding execution context for a single datadir.
    """

    datadir = Path(datadir)
    datadir_rulefile = datadir / DATADIR_RULEFILE_NAME
    datadir_configfile = datadir / DATADIR_CONFIGFILE_NAME
    is_self_contained = (datadir / DATADIR_CONFIGFILE_NAME).is_file()

    if is_self_contained:
        configfile_used = datadir_configfile
    else:
        configfile_used = repo_configfile  # As passed in; this could be None.

    # Config rootdir is used for resolving relative paths in the config universe.
    # It is the directory that contains config file actually used.
    # When no config file exists, config rootdir defaults to Datadir.
    if configfile_used is None:
        config_rootdir = datadir
    else:
        config_rootdir = configfile_used.parent

    # If Datadir is self-contained (config root is itself), ignore repo-level rules.
    if (not is_self_contained) and repo_rulefile is not None:
        rulefiles_used = [repo_rulefile, datadir_rulefile]
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
