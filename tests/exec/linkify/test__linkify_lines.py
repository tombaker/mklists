"""Tests for $MKLMKL/exec/linkify.py"""

from mklists.exec.linkify import _linkify_lines


def test_linkify_lines_no_urls():
    """Plain text is wrapped in a single <pre> block."""
    text = "alpha\nbeta\ngamma\n"
    result = _linkify_lines(text)
    assert result == "<pre>\nalpha\nbeta\ngamma\n</pre>\n"


def test_linkify_lines_with_url():
    """URLs inside text are converted to anchor tags."""
    text = "see https://example.com for details\n"
    result = _linkify_lines(text)
    assert '<a href="https://example.com">https://example.com</a>' in result
    assert result.startswith("<pre>\n")
    assert result.endswith("\n</pre>\n")


def test_linkify_lines_no_trailing_blank_line():
    """No blank line appears immediately before </pre>."""
    text = "line one\nline two\n"
    result = _linkify_lines(text)
    assert "\n\n</pre>" not in result
