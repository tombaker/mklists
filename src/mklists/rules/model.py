"""Load and validate transformation rules for a given data directory."""

from dataclasses import dataclass
from typing import Iterable, Pattern


@dataclass(frozen=True)
class Rule:
    """Immutable data structure for one validated rule."""

    source_matchfield: int
    source_matchpattern: Pattern[str]
    source: str
    target: str
    target_sortkey: int | None
