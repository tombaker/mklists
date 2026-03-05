"""@@@"""


def linkify_datadirs(datadirs, linkifydir):
    """@@@"""
    print(datadirs)
    print(html_dir)


import re

URL_RE = re.compile(r"(https?://[^\s<>()]+)([.,;:!?)]?)")


def _replace_url(match: re.Match) -> str:
    """Convert a detected URL into an HTML link while preserving punctuation."""
    url = match.group(1)
    punctuation = match.group(2)

    link = f'<a href="{url}">{url}</a>'
    return link + punctuation


def linkify_lines(text: str) -> str:
    """Wrap lines in <pre> and convert URLs into clickable HTML links."""
    linked_text = URL_RE.sub(_replace_url, text)

    return "<pre>\n" + linked_text + "\n</pre>\n"
