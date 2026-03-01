"""Filesystem-derived structural context for a Mklists run."""

from dataclasses import dataclass
from pathlib import Path
from mklists.rules.model import Rule


@dataclass(frozen=True, slots=True)
class DatadirStructuralContext:
    """Filesystem-derived context for one datadir."""

    datadir: Path
    datadir_configfile_found: Path | None
    datadir_rulefile: Path


@dataclass(frozen=True, slots=True)
class StartdirStructuralContext:
    """Filesystem-derived context for starting directory."""

    startdir: Path
    repo_configfile_found: Path | None
    repo_rulefile_found: Path | None


@dataclass(frozen=True, slots=True)
class StructuralContext:
    """Structural context as derived from filesystem layout."""

    startdir_context: StartdirStructuralContext
    datadir_contexts: list[DatadirStructuralContext]
