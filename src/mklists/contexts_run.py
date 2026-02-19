"""Resolve execution context for a single run."""

from dataclasses import dataclass
from operator import attrgetter
from pathlib import Path
from .contexts_datadir import DatadirContext, resolve_datadir_context
from .structure import DATADIR_RULEFILE_NAME, REPO_CONFIGFILE_NAME, REPO_RULEFILE_NAME


@dataclass(slots=True)
class RunContext:
    """Resolved execution context for a single run."""

    rundir: Path
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
        ├── determine rundir
        ├── detect repo-level config + rulefile
        ├── discover datadirs
        └── resolve_datadir_context(...) for each
                ↓
            produce list[DatadirContext]
    contexts_run.py
    """
    startdir = Path(startdir).resolve()

    # ------------------------------------------------------------
    # 1. Determine repo-level markers
    # ------------------------------------------------------------
    repo_configfile = _find_repo_configfile(startdir)
    repo_rulefile = _find_repo_rulefile(startdir)

    # Decide effective rundir (repo root or single datadir mode)
    rundir = _determine_rundir(
        startdir=startdir,
        repo_configfile=repo_configfile,
        repo_rulefile=repo_rulefile,
    )

    # ------------------------------------------------------------
    # 2. Discover datadirs
    # ------------------------------------------------------------
    datadir_paths = _find_datadirs(rundir)

    if not datadir_paths:
        raise RuntimeError("No datadirs found under repository root.")

    # ------------------------------------------------------------
    # 3. Resolve each DatadirContext
    # ------------------------------------------------------------
    datadir_contexts: list[DatadirContext] = []

    for datadir in datadir_paths:
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
        rundir=rundir,
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


def _determine_rundir(
    *,
    startdir: Path,
    repo_configfile: Path | None,
    repo_rulefile: Path | None,
) -> Path:
    """Determine effective run directory.

    Returns:
        Path to repository root (even in single-datadir mode).

    Raises:
        RuntimeError if structure is invalid.
    """

    datadir_rulefile = startdir / DATADIR_RULEFILE_NAME
    is_datadir = datadir_rulefile.is_file()
    is_repo_root = repo_configfile is not None or repo_rulefile is not None

    # Structural invariant: cannot be both
    if is_datadir and is_repo_root:
        raise RuntimeError("Directory cannot be both repository root and datadir.")

    # Repo mode
    if is_repo_root:
        return startdir

    # Single-datadir convenience mode
    if is_datadir:
        return startdir

    raise RuntimeError("Directory is neither repository root nor datadir.")
