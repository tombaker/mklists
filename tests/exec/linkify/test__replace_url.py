"""Tests for $MKLMKL/exec/linkify.py"""

from mklists.exec.linkify import _replace_url


def test_replace_url_no_punctuation(mocker):
    """URL with no trailing punctuation is wrapped in an anchor tag."""
    m = mocker.Mock()
    m.group.side_effect = lambda n: {1: "https://example.com", 2: ""}[n]
    assert _replace_url(m) == '<a href="https://example.com">https://example.com</a>'


def test_replace_url_trailing_period(mocker):
    """Trailing period is placed after the anchor tag, not inside the href."""
    m = mocker.Mock()
    m.group.side_effect = lambda n: {1: "https://example.com", 2: "."}[n]
    assert _replace_url(m) == '<a href="https://example.com">https://example.com</a>.'


def test_replace_url_trailing_comma(mocker):
    """Trailing comma is placed after the anchor tag."""
    m = mocker.Mock()
    m.group.side_effect = lambda n: {1: "https://example.com", 2: ","}[n]
    assert _replace_url(m) == '<a href="https://example.com">https://example.com</a>,'
