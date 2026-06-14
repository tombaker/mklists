"""Tests $MKLMKL/exec/process_datalines.py"""

import pytest
from mklists.exec.process_datalines import _sort_datalines
from mklists.rules.model import SortKey


def test_sort_datalines_none_sortkey_returns_input_unchanged():
    """Sort key of None means no sorting."""
    datalines = ["b 2", "a 1", "c 3"]
    result = _sort_datalines(datalines, None)
    assert result == datalines


def test_sort_datalines_zero_sorts_on_entire_line():
    """Sort key of zero means sort on entire line."""
    datalines = ["b 2", "a 10", "a 2"]
    result = _sort_datalines(datalines, [SortKey(field=0)])
    assert result == ["a 10", "a 2", "b 2"]


def test_sort_datalines_onebased_field_sort():
    """Positive sort key means sorting on nth field (one-based)."""
    datalines = ["b 2", "a 10", "a 1"]
    result = _sort_datalines(datalines, [SortKey(field=1)])
    assert result == ["a 10", "a 1", "b 2"]


def test_sort_datalines_missing_fields_sort_first():
    """Missing fields sort first on basis of empty string."""
    datalines = ["b", "a 2", "c 3"]
    result = _sort_datalines(datalines, [SortKey(field=2)])
    assert result == ["b", "a 2", "c 3"]


def test_sort_datalines_is_stable_for_equal_keys():
    """Sorting is stable when all sort-key values are identical across lines."""
    datalines = ["a x", "b x", "c x"]
    result = _sort_datalines(datalines, [SortKey(field=2)])
    assert result == ["a x", "b x", "c x"]


def test_sort_datalines_onebased_indexing_not_zerobased():
    """Function is passed onebased index, not zerobased."""
    datalines = ["x a", "y b", "z c"]
    result = _sort_datalines(datalines, [SortKey(field=2)])
    assert result == ["x a", "y b", "z c"]


def test_sort_datalines_multikey_primary_then_secondary():
    """Primary key groups; secondary key orders within each group."""
    datalines = [
        "bookmark FLATSRAP /path/FLATSRAP",
        "filehandle :Ctrb /path/CTRB/index.md",
        "bookmark CTRB /path/CTRB",
        "filehandle :Flatsrap /path/FLATSRAP/index.md",
    ]
    result = _sort_datalines(datalines, [SortKey(field=1), SortKey(field=3)])
    assert result == [
        "bookmark CTRB /path/CTRB",
        "bookmark FLATSRAP /path/FLATSRAP",
        "filehandle :Ctrb /path/CTRB/index.md",
        "filehandle :Flatsrap /path/FLATSRAP/index.md",
    ]


def test_sort_datalines_reverse_modifier():
    """Modifier r reverses sort order."""
    datalines = ["a 1", "b 2", "c 3"]
    result = _sort_datalines(datalines, [SortKey(field=1, reverse=True)])
    assert result == ["c 3", "b 2", "a 1"]


def test_sort_datalines_numeric_modifier_sorts_by_value_not_lexicographic():
    """Modifier n compares as numbers, not strings."""
    datalines = ["x 10", "x 2", "x 1"]
    result = _sort_datalines(datalines, [SortKey(field=2, numeric=True)])
    assert result == ["x 1", "x 2", "x 10"]


def test_sort_datalines_casefold_modifier():
    """Modifier f makes sort case-insensitive."""
    datalines = ["Beta one", "alpha two", "GAMMA three"]
    result = _sort_datalines(datalines, [SortKey(field=1, casefold=True)])
    assert result == ["alpha two", "Beta one", "GAMMA three"]


def test_sort_datalines_reverse_numeric_combined():
    """Modifiers r and n may be combined."""
    datalines = ["x 1", "x 10", "x 2"]
    result = _sort_datalines(datalines, [SortKey(field=2, reverse=True, numeric=True)])
    assert result == ["x 10", "x 2", "x 1"]


def test_sort_datalines_multikey_with_reverse_on_secondary():
    """Secondary key can be reversed independently of primary."""
    datalines = [
        "a 3",
        "b 1",
        "a 1",
        "b 3",
    ]
    result = _sort_datalines(
        datalines, [SortKey(field=1), SortKey(field=2, reverse=True)]
    )
    assert result == ["a 3", "a 1", "b 3", "b 1"]
