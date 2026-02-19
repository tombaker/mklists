"""Resolve execution context for a single datadir."""

from dataclasses import dataclass
from pathlib import Path
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
    contexts_datadir.py
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
        configfile_used=configfile_used,
    )

    # 4. Parse rules
    rules = load_rules_for_datadir(rulefile_paths)

    return DatadirContext(
        datadir=datadir,
        configfile_used=configfile_used,
        rules=rules,
    )


def _find_datadir_configfile(dirpath: Path) -> Path | None:
    """Return datadir config file if present in dirpath."""
    candidate = dirpath / DATADIR_CONFIGFILE_NAME
    return candidate if candidate.is_file() else None


def _find_datadir_rulefile(dirpath: Path) -> Path | None:
    """Return repo rulefile if present in dirpath."""
    candidate = dirpath / DATADIR_RULEFILE_NAME
    return candidate if candidate.is_file() else None


def _resolve_effective_rulefiles(
    datadir_rulefile: Path | None,
    repo_rulefile: Path | None,
    configfile_used: Path | None,
) -> list[Path]:
    """@@@"""
    # pylint: disable=unused-argument
    effective_rulefiles: list[Path] = []
    return effective_rulefiles
