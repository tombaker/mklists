"""Dispatch datalines to new targets.

Take flat list of datalines,
use rules to partition and reroute,
map new filenames to new datalines.

Dispatch lines according to rules,
with fan-out behavior and routing semantics.
"""

import re
from typing import Pattern
from .rules import Rule


class DataNotFoundError(ValueError):
    """Base class for errors with lists of data lines."""


class RulesNotFoundError(ValueError):
    """No rules were found."""


def dispatch_datalines_to_targets(
    rules: list[Rule],
    datalines: list[str],
) -> dict[str, list[str]]:
    """Applies rules to build dictionary mapping filenames to lists of datalines.

    Args:
        rules: List of Rule objects.
        datalines: List of lines from data files.

    Returns:
        Dictionary mapping filenames to lists of data lines.
    """
    if not rules:
        raise RulesNotFoundError("No rules specified.")

    if not datalines:
        raise DataNotFoundError("No data specified.")

    all_keys = set()
    for rule in rules:
        all_keys.add(rule.source)
        all_keys.add(rule.target)

    lines_dict: dict[str, list[str]] = {key: [] for key in all_keys}
    # Before any rules are applied, all data belongs to the initial source.
    lines_dict[rules[0].source] = datalines

    for rule in rules:
        matched = []
        unmatched = []
        for line in lines_dict[rule.source]:
            if _dataline_matches_pattern(
                dataline=line,
                pattern=rule.source_matchpattern,
                onebased_matchfield=rule.source_matchfield,
            ):
                matched.append(line)
            else:
                unmatched.append(line)

        lines_dict[rule.source] = unmatched
        lines_dict[rule.target].extend(matched)

        target_lines = lines_dict[rule.target]
        sortkey = rule.target_sortkey
        lines_dict[rule.target] = _sort_datalines(
            datalines=target_lines,
            onebased_sortkey=sortkey,
        )

    return lines_dict


def _dataline_matches_pattern(
    dataline: str,
    pattern: Pattern[str],
    onebased_matchfield: int,
) -> bool:
    """Return True if given field in data line matches regex.

    Args:
        dataline:
        pattern:
        onebased_matchfield:

    Returns:
        True if given field in data line matches regex.

    Note:
        Match field of 0 matches against entire line.
        Positive match field matches against nth whitespace-delimited field.
    """
    ruleline_fields = dataline.split()

    if onebased_matchfield < 0:
        return False

    if onebased_matchfield == 0:
        if re.search(pattern, dataline):
            return True

        return False

    if onebased_matchfield > len(ruleline_fields):
        return False

    if re.search(pattern, ruleline_fields[onebased_matchfield - 1]):
        return True

    return False


def _sort_datalines(datalines: list[str], onebased_sortkey: int | None) -> list[str]:
    """Return datalines sorted by a one-based field index.

    Args:
        datalines: List of lines.
        onebased_sortkey: Sort key (one-based field number, as in Awk).

    Returns:
        Sorted list of lines.

    Note:
        Sort key `0` sorts on entire line, not a specific field (analogously to Awk).
    """
    if onebased_sortkey is None:
        return datalines

    if onebased_sortkey == 0:
        return sorted(datalines)

    zerobased = onebased_sortkey - 1

    def sortkey_fn(line: str) -> str:
        """Compute sort text using zero-based field index captured from closure."""
        ruleline_fields = line.split()
        if zerobased >= len(ruleline_fields):
            return ""

        return ruleline_fields[zerobased]

    return sorted(datalines, key=sortkey_fn)
