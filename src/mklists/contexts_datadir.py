"""Resolve execution context for a single datadir."""

from dataclasses import dataclass
from pathlib import Path
from .errors import StructureError
from .rules import Rule, load_rules_for_datadir
from .structure import DATADIR_CONFIGFILE_NAME, DATADIR_RULEFILE_NAME


@dataclass(slots=True)
class DatadirContext:
    """Resolved execution context for a single Datadir."""

    datadir: Path
    configfile_used: Path | None
    rules: list[Rule]


def resolve_datadir_context(
    *,
    datadir: Path,
    repo_configfile: Path | None,
    repo_rulefile: Path | None,
) -> DatadirContext:
    """Resolve execution context for a single datadir.

    Args:
        datadir:
        repo_configfile:
        repo_rulefile:

    Returns:
        DatadirContext object holding execution context for a single datadir.
    """

    datadir = Path(datadir)

    # 1. Detect local markers
    datadir_configfile = _find_datadir_configfile(datadir)
    datadir_rulefile = _find_datadir_rulefile(datadir)

    # 2. Determine effective configfile
    configfile_used = (
        datadir_configfile if datadir_configfile is not None else repo_configfile
    )

    # 3. Determine effective rulefiles
    rulefile_paths = _resolve_effective_rulefiles(
        datadir_rulefile=datadir_rulefile,
        repo_rulefile=repo_rulefile,
    )

    # 4. Parse rules
    rules = load_rules_for_datadir(rulefile_paths)

    return DatadirContext(
        datadir=datadir,
        configfile_used=configfile_used,
        rules=rules,
    )


def _find_datadir_configfile(datadir: Path) -> Path | None:
    """Return datadir config file if present in datadir.

    Args:
        datadir: Path of datadir.

    Return:
        Path of datadir configfile, if present.
    """
    candidate = datadir / DATADIR_CONFIGFILE_NAME

    return candidate if candidate.is_file() else None


def _find_datadir_rulefile(datadir: Path) -> Path | None:
    """Return datadir rulefile if present in datadir.

    Args:
        datadir: Path of datadir.

    Return:
        Path of datadir rootfile, if present.
    """
    candidate = datadir / DATADIR_RULEFILE_NAME

    return candidate if candidate.is_file() else None


def _resolve_effective_rulefiles(
    *,
    datadir_rulefile: Path | None,
    repo_rulefile: Path | None,
) -> list[Path]:
    """Determine ordered list of rulefiles for a datadir.

    Args:
        datadir_rulefile: Path to datadir-level rule file.
        repo_rulefile: Path repo-level rule file, if present.

    Returns:
        List of rulefile paths in application order:
            1. Repo-level rulefile `mklists.rules` (if present)
            2. Datadir-level rulefile `.rules` (required)

    Raises:
        StructureError: If datadir_rulefile is None.

    Note:
        This function only determines rulefile order.
        Validation of concatenated chain is performed by rules module.
    """
    if datadir_rulefile is None:
        raise StructureError("Datadir must contain a rulefile.")

    effective_rulefiles: list[Path] = []

    if repo_rulefile is not None:
        effective_rulefiles.append(repo_rulefile)

    effective_rulefiles.append(datadir_rulefile)

    return effective_rulefiles

