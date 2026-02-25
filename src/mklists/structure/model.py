"""@@@"""

from dataclasses import dataclass
from pathlib import Path
from mklists.rules.model import Rule

@dataclass(slots=True)
class DatadirContext:
    """Resolved execution context for a single Datadir."""

    datadir: Path
    configfile_used: Path | None
    rules: list[Rule]


@dataclass(slots=True)
class DatadirStructuralContext:
    """Filesystem-derived context for one datadir."""

    datadir: Path

    # What was actually discovered / selected
    configfile_found: Path | None          # eg datadir/.mklistsrc if present
    configfile_used: Path | None           # after inheritance rules
    rulefiles_found: list[Path]            # eg [parent/mklists.rules, datadir/.rules]
    rulefiles_used: list[Path]             # after 'self-contained' rules

    # Materialized structural results
    rules: list[Rule]                      # parsed + validated from rulefiles_used


@dataclass(slots=True)
class StructuralContext:
    """Structural context as derived from filesystem layout."""

    config_rootdir: Path
    repo_configfile: Path | None
    repo_rulefile: Path | None
    datadir_contexts: list[DatadirContext]
