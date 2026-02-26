"""@@@"""

from dataclasses import dataclass
from pathlib import Path
from mklists.rules.model import Rule


@dataclass(slots=True)
class DatadirStructuralContext:
    """Filesystem-derived context for one datadir."""

    datadir: Path
    configfile_used: Path | None  # after inheritance rules
    config_rootdir: Path
    rulefiles_used: list[Path]  # after 'self-contained' rules
    rules: list[Rule]  # parsed + validated from rulefiles_used


@dataclass(slots=True)
class StructuralContext:
    """Structural context as derived from filesystem layout."""

    config_rootdir: Path
    repo_configfile: Path | None
    repo_rulefile: Path | None
    datadir_contexts: list[DatadirStructuralContext]
