"""Filesystem-derived structural context for a Mklists run."""

from dataclasses import dataclass
from pathlib import Path
from mklists.errors import StructureError


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
    datadir_configfile_found: Path | None
    datadir_rulefile_found: Path | None

    @property
    def is_repo_root(self) -> bool:
        """Startdir is root directory of a repository of datadirs."""
        return bool(self.repo_configfile_found or self.repo_rulefile_found)

    @property
    def is_datadir_selfcontained(self) -> bool:
        """Startdir is a self-contained datadir."""
        return bool(self.datadir_rulefile_found and self.datadir_configfile_found)

    @property
    def is_datadir_in_repo(self) -> bool:
        """Startdir is a datadir within a repository of datadirs."""
        return bool(self.datadir_rulefile_found and not self.datadir_configfile_found)

    @property
    def config_rootdir(self) -> Path:
        """Base directory for resolving relative paths in config universe."""
        if self.is_repo_root or self.is_datadir_selfcontained:
            return self.startdir

        if self.is_datadir_in_repo:
            return self.startdir.parent

        raise StructureError("Unreachable structural state.")


@dataclass(frozen=True, slots=True)
class StructuralContext:
    """Structural context as derived from filesystem layout."""

    startdir_context: StartdirStructuralContext
    datadir_contexts: list[DatadirStructuralContext]
