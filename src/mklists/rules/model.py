"""Load and validate transformation rules for a given data directory."""

from dataclasses import dataclass
from typing import Pattern


@dataclass(frozen=True)
class SortKey:
    """One sort key: a field number plus optional modifiers."""

    field: int
    reverse: bool = False
    numeric: bool = False
    casefold: bool = False


@dataclass(frozen=True)
class Rule:
    """Immutable data structure for one validated rule."""

    source_matchfield: int
    source_matchpattern: Pattern[str]
    source: str
    target: str
    target_sortkeys: list[SortKey] | None
