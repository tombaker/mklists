"""Tests for $MKLMKL/exec/linkify.py

replace_url receives a re.Match object and calls .group(1) and .group(2) on it.

Constructing a real re.Match requires running an actual regex against a string, 
which would couple the test to URL_RE internals. 

Instead, mocker.Mock() creates a lightweight stand-in 
whose .group() method is given a side_effect — 
a lambda that returns controlled values keyed by argument — 
so each test can specify exactly the URL and punctuation it wants to exercise, 
independently of the regex.
"""

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
