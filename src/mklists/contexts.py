"""Resolution of run contexts

In Mklists, a directory is interpreted structurally as either a Repo Root
or a Datadir. A Repo Root is defined by the presence of `mklists.yaml`
and/or `mklists.rules`; a Datadir is defined by the presence of `.rules`.
A directory may not be both.

Configuration files (`mklists.yaml` or `.mklistsrc`) define global
execution context and are directly relevant to processing the directory
in which they are found. Rule files, however, are applied only when
processing a Datadir. A Repo Root is not itself processed as a Datadir;
instead, it serves as an orchestration point from which Datadirs are
discovered and processed individually. For this reason, the RunContext
for a Repo Root never includes rule_files, even if `mklists.rules`
exists in that directory.

Datadirs may inherit configuration and rule files only from their
immediate parent Repo Root unless they contain `.mklistsrc`, which
makes them self-contained and prevents inheritance.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from operator import attrgetter
from pathlib import Path
from .config import REPO_CONFIGFILE_NAME, DATADIR_CONFIGFILE_NAME
from .rules import REPO_RULEFILE_NAME, DATADIR_RULEFILE_NAME, load_rules_for_datadir


@dataclass(slots=True)
class DatadirContext:
    """Resolved execution context for a single Datadir."""

    datadir_path: Path
    configfile_path: Path | None
    rules: list[Rule]


@dataclass(slots=True)
class RunContext:
    """Resolved execution context for a single run."""
    rundir: Path
    repo_configfile: Path | None
    repo_rulefile: Path | None
    datadirs: list[DatadirContext]


def resolve_run_context(startdir: Path) -> RunContext:
    """Resolve execution context for one run.

    Args:
        startdir:

    Returns:
        Execution context for one run as RunContext object.
    """
    startdir = Path(startdir)

    datadir_rules = startdir / DATADIR_RULEFILE_NAME
    is_datadir = datadir_rules.is_file()

    repo_configfile = startdir / REPO_CONFIGFILE_NAME
    if not repo_configfile.is_file():
        repo_configfile = None

    repo_rulefile = startdir / REPO_RULEFILE_NAME
    if not repo_rulefile.is_file():
        repo_rulefile = None

    is_repo_root = repo_configfile or repo_rulefile

    # ----- violation of disjointness ---------------------------------
    if is_repo_root and is_datadir:
        raise RuntimeError(f"{startdir} cannot be both Repo Root and Datadir.")

    # ----- invalid invocation ----------------------------------------
    if not (is_repo_root or is_datadir):
        raise RuntimeError(f"{startdir} is neither Repo Root nor Datadir.")

    # ================================================================
    # Case 1 → startdir is repo root → discover datadirs
    # ================================================================
    if is_repo_root:
        datadirs = _find_datadirs(repodir=startdir)

        return RunContext(
            rundir=startdir,
            datadirs=datadirs,
        )

    # ================================================================
    # Case 2 → startdir is exactly one datadir
    # ================================================================
    datadirs = [startdir]

    return RunContext(
        rundir=startdir,
        repo_configfile=repo_configfile,
        repo_rulefile=repo_rulefile,
        datadirs=datadirs,
    )


def resolve_datadir_contexts(run_context: RunContext) -> list[DatadirContext]:
    """Return execution contexts for Datadirs to be processed in this run.

    Args:
        run_context: RunContext object that holds execution context for one run.

    Returns:
        List of execution contexts for Datadirs as DatadirContext objects.

    rundir == repodir
    OR
    rundir == datadir
    """
    contexts: list[DatadirContext] = []

    rundir = run_context.rundir

    # ----------------------------------------------------------------
    # Build a DatadirContext for each datadir
    # ----------------------------------------------------------------
    for datadir in run_context.datadirs:
        datadir_rules = datadir / DATADIR_RULEFILE_NAME
        datadir_config = datadir / DATADIR_CONFIGFILE_NAME

        is_selfcontained = datadir_config.is_file()

        rulefile_paths: list[Path] = []

        if is_selfcontained:
            config_file = datadir_config
            rulefile_paths = [datadir_rules]
        else:
            config_file = run_context.repo_configfile

            if run_context.repo_rulefile:
                rulefile_paths.append(repo_rulefile)

            rulefile_paths.append(datadir_rules)

        # ---- load rules ---------------------------------------------
        rules = load_rules_for_datadir(rulefile_paths)

        contexts.append(
            DatadirContext(
                datadir_path=datadir,
                configfile_path=config_file,
                rules=rules,
            )
        )

    return contexts


def _find_datadirs(repodir: Path | str) -> Iterable[Path]:
    """Yields paths of data directories under repository root.

    Args:
        repodir: Root of Mklists repository tree.

    Yields:
        Paths of directories directly under repository root that hold a `.rules` file.
    """
    datadirs = [
        entry
        for entry in repodir.iterdir()
        if entry.is_dir() and (entry / ".rules").is_file()
    ]

    yield from sorted(datadirs, key=attrgetter("name"))
