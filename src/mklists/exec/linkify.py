"""Mirror datadirs as URL-linkified files for browsing on GitHub or a web server."""

import re
import shutil
from pathlib import Path

from mklists.logging import logger

URL_RE = re.compile(r"((?:https?|file)://[^\s<>()]*[^\s<>().,;:!?)])([.,;:!?)]?)")


def linkify_md_datadirs(datadirs: list[Path], linkify_md_dir: Path) -> None:
    """Mirror datadirs to linkify_md_dir with URL-linkified .md files.

    Each visible data file is written as <filename>.md — HTML-in-Markdown
    wrapped in a <pre> block with URLs as <a> tags. GitHub renders .md files
    and passes through these tags, making links clickable when browsing the
    repository.

    Args:
        datadirs: List of datadir paths.
        linkify_md_dir: Root of mirror directory tree for .md output.

    Returns:
        None, after mirroring datadirs under linkify_md_dir.
    """
    logger.info(f"Linkify to {linkify_md_dir}")
    _mirror_datadirs(datadirs=datadirs, output_dir=linkify_md_dir, suffix=".md")


def linkify_html_datadirs(datadirs: list[Path], linkify_html_dir: Path) -> None:
    """Mirror datadirs to linkify_html_dir with URL-linkified .html files.

    Each visible data file is written as <filename>.html — a <pre> block with
    URLs as <a> tags. Any web server (including Dropbox) will serve these as
    rendered HTML with clickable links.

    Args:
        datadirs: List of datadir paths.
        linkify_html_dir: Root of mirror directory tree for .html output.

    Returns:
        None, after mirroring datadirs under linkify_html_dir.
    """
    logger.info(f"Linkify to {linkify_html_dir}")
    _mirror_datadirs(datadirs=datadirs, output_dir=linkify_html_dir, suffix=".html")


def _mirror_datadirs(datadirs: list[Path], output_dir: Path, suffix: str) -> None:
    """Write URL-linkified copies of all datafiles under output_dir.

    Supported layouts (no deeper nesting):
    - Flat: one datadir that is config_rootdir; files land in output_dir directly.
    - Subdir: multiple datadirs one level under config_rootdir; each maps to
      output_dir/<datadir_name>/.

    All existing content under output_dir is deleted before writing, so stale
    files and directories from previous runs are always removed.

    Args:
        datadirs: List of datadir paths.
        output_dir: Root of mirror directory tree.
        suffix: File extension to append to each mirrored filename (.md or .html).

    Returns:
        None, after mirroring datadirs under output_dir with linkified datafiles.
    """
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    config_rootdir = datadirs[0] if len(datadirs) == 1 else datadirs[0].parent

    for datadir in datadirs:
        rel = datadir.relative_to(config_rootdir)
        mirror_dir = output_dir / rel
        mirror_dir.mkdir(parents=True, exist_ok=True)

        for datafile in sorted(datadir.iterdir()):
            if datafile.name.startswith(".") or not datafile.is_file():
                continue
            text = datafile.read_text(encoding="utf-8")
            content = _linkify_lines(text)
            (mirror_dir / (datafile.name + suffix)).write_text(
                content, encoding="utf-8"
            )


def _linkify_lines(text: str) -> str:
    """Wrap text in <pre> and convert URLs into clickable HTML links.

    Args:
        text: Plain text, possibly containing URLs and trailing newlines.

    Returns:
        Text wrapped in a ``<pre>`` block with URLs converted to ``<a>`` tags.

    Note:
        URLs that genuinely end with ``.,;:!?)`` will have that character
        incorrectly stripped; this is rare compared with prose punctuation
        following a URL. Example:
        https://en.wikipedia.org/wiki/DOT_(graph_description_language)

    Examples:
        >>> _linkify_lines("See https://foo.com details.")
        '<pre>\\nSee <a href="https://foo.com">https://foo.com</a> details.\\n</pre>\\n'

        >>> _linkify_lines("No URLs here.")
        '<pre>\\nNo URLs here.\\n</pre>\\n'

        >>> _linkify_lines("See file:///foo/bar here.")
        '<pre>\\nSee <a href="file:///foo/bar">file:///foo/bar</a> here.\\n</pre>\\n'
    """
    linked_text = URL_RE.sub(_replace_url, text)
    return "<pre>\n" + linked_text.rstrip("\n") + "\n</pre>\n"


def _replace_url(match: re.Match) -> str:
    """Convert a detected URL into an HTML link while preserving punctuation.

    Args:
        match: A `re.Match` object.

    Returns:
        String in which URL has been wrapped in <a> tags.

    Examples:
        >>> m = URL_RE.match("https://foo.com.")
        >>> _replace_url(m)
        '<a href="https://foo.com">https://foo.com</a>.'

        >>> m = URL_RE.match("https://foo.com/path")
        >>> _replace_url(m)
        '<a href="https://foo.com/path">https://foo.com/path</a>'
    """
    url = match.group(1)
    punctuation = match.group(2)
    return f'<a href="{url}">{url}</a>' + punctuation
