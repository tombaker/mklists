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
    datatree_configfile_found: Path | None
    datatree_rulefile_found: Path | None
    datadir_configfile_found: Path | None
    datadir_rulefile_found: Path | None

    @property
    def is_datatree_root(self) -> bool:
        """True if startdir is the root directory of a datatree."""
        return bool(self.datatree_configfile_found or self.datatree_rulefile_found)

    @property
    def is_datadir_selfcontained(self) -> bool:
        """True if startdir is a self-contained datadir."""
        return bool(self.datadir_rulefile_found and self.datadir_configfile_found)

    @property
    def is_datadir_in_datatree(self) -> bool:
        """True if startdir is a datadir within a datatree."""
        return bool(self.datadir_rulefile_found and not self.datadir_configfile_found)

    @property
    def config_rootdir(self) -> Path:
        """Base directory for resolving relative paths in config universe."""
        if self.is_datatree_root or self.is_datadir_selfcontained:
            return self.startdir

        if self.is_datadir_in_datatree:
            return self.startdir.parent

        raise StructureError("Unreachable structural state.")


@dataclass(frozen=True, slots=True)
class StructuralContext:
    """Structural context as derived from filesystem layout."""

    startdir_context: StartdirStructuralContext
    datadir_contexts: list[DatadirStructuralContext]
