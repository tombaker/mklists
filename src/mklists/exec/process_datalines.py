"""Dispatch datalines to new targets.

Take flat list of datalines,
use rules to partition and reroute,
map new filenames to new datalines.

Dispatch lines according to rules,
with fan-out behavior and routing semantics.
"""

import functools
import re
from typing import Pattern

from mklists.errors import DataNotFoundError, RulesNotFoundError
from mklists.rules import Rule
from mklists.rules.model import SortKey


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
        lines_dict[rule.target] = _sort_datalines(
            datalines=target_lines,
            sortkeys=rule.target_sortkeys,
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


def _sort_datalines(datalines: list[str], sortkeys: list[SortKey] | None) -> list[str]:
    """Return datalines sorted by an ordered list of sort keys.

    Args:
        datalines: List of lines.
        sortkeys: Ordered list of SortKey objects, or None for no sorting.

    Returns:
        Sorted list of lines.

    Note:
        Field numbers are one-based (as in Awk); field 0 sorts on the entire line.
        Missing fields compare as empty string.
    """
    if sortkeys is None:
        return datalines

    def compare(a: str, b: str) -> int:
        af = a.split()
        bf = b.split()
        for sk in sortkeys:
            if sk.field == 0:
                av: str = a
                bv: str = b
            else:
                idx = sk.field - 1
                av = af[idx] if idx < len(af) else ""
                bv = bf[idx] if idx < len(bf) else ""
            if sk.casefold:
                av, bv = av.casefold(), bv.casefold()
            if sk.numeric:
                try:
                    lt = float(av) < float(bv)
                    gt = float(av) > float(bv)
                except ValueError:
                    lt = av < bv
                    gt = av > bv
            else:
                lt = av < bv
                gt = av > bv
            if lt:
                return 1 if sk.reverse else -1
            if gt:
                return -1 if sk.reverse else 1
        return 0

    return sorted(datalines, key=functools.cmp_to_key(compare))
