"""Resolve execution context for a single run."""

from dataclasses import dataclass
from operator import attrgetter
from pathlib import Path
from ..errors import StructureError
from .contexts_datadir import DatadirContext, resolve_datadir_context
from .structure import DATADIR_RULEFILE_NAME, REPO_CONFIGFILE_NAME, REPO_RULEFILE_NAME


@dataclass(slots=True)
class RunContext:
    """Resolved execution context for a single run."""

    config_rootdir: Path
    repo_configfile: Path | None
    repo_rulefile: Path | None
    datadir_contexts: list[DatadirContext]


def resolve_run_context(startdir: Path | str) -> RunContext:
    """Resolve full filesystem execution context for one run.

    Args:
        startdir:

    Returns:
        Execution context for one run as RunContext object.

    resolve_run_context
        ├── determine config_rootdir
        ├── detect repo-level config + rulefile
        ├── discover datadirs
        └── resolve_datadir_context(...) for each
                ↓
            produce list[DatadirContext]
    """
    startdir = Path(startdir).resolve()

    # 1. Determine repo-level markers
    repo_configfile = _find_repo_configfile(startdir)
    repo_rulefile = _find_repo_rulefile(startdir)

    # Decide effective config_rootdir (repo root or single datadir)
    config_rootdir = _determine_config_rootdir(
        startdir=startdir,
        repo_configfile=repo_configfile,
        repo_rulefile=repo_rulefile,
    )

    # 2. Discover datadirs
    datadirs = _find_datadirs(config_rootdir)

    if not datadirs:
        raise StructureError("No datadirs found under repository root.")

    # 3. Resolve each DatadirContext
    datadir_contexts: list[DatadirContext] = []

    for datadir in datadirs:
        context = resolve_datadir_context(
            datadir=datadir,
            repo_configfile=repo_configfile,
            repo_rulefile=repo_rulefile,
        )
        datadir_contexts.append(context)

    # ------------------------------------------------------------
    # 4. Emit fully resolved RunContext
    # ------------------------------------------------------------
    return RunContext(
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
