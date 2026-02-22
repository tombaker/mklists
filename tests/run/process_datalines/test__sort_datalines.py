"""Tests $MKLRUN/process_datalines.py"""

import pytest
from mklists.run.process_datalines import _sort_datalines


def test_sort_datalines_none_sortkey_returns_input_unchanged():
    """Sort key of None means no sorting."""
    datalines = ["b 2", "a 1", "c 3"]
    result = _sort_datalines(datalines, None)
    assert result == datalines


def test_sort_datalines_zero_sorts_on_entire_line():
    """Sort key of zero means sort on entire line."""
    datalines = ["b 2", "a 10", "a 2"]
    result = _sort_datalines(datalines, 0)
    assert result == ["a 10", "a 2", "b 2"]


def test_sort_datalines_onebased_field_sort():
    """Positive sort key means sorting on nth field (one-based)."""
    datalines = ["b 2", "a 10", "a 1"]
    result = _sort_datalines(datalines, 1)
    assert result == ["a 10", "a 1", "b 2"]


def test_sort_datalines_missing_fields_sort_first():
    """Missing fields sort first on basis of empty string."""
    datalines = ["b", "a 2", "c 3"]
    result = _sort_datalines(datalines, 2)
    assert result == ["b", "a 2", "c 3"]


def test_sort_datalines_is_stable_for_equal_keys():
    """Sorting is stable, preserving original order of non-sorting fields."""
    datalines = ["a 2", "a 1", "a 3"]
    result = _sort_datalines(datalines, 1)
    assert result == ["a 2", "a 1", "a 3"]


def test_sort_datalines_onebased_indexing_not_zerobased():
    """Function is passed onebased index, not zerobased."""
    datalines = ["x a", "y b", "z c"]
    result = _sort_datalines(datalines, 2)
    assert result == ["x a", "y b", "z c"]
