"""Mirror datadirs as URL-linkified Markdown files for GitHub rendering."""

import re
import shutil
from pathlib import Path

URL_RE = re.compile(r"(https?://[^\s<>()]+)([.,;:!?)]?)")


def linkify_datadirs(datadirs: list[Path], linkify_dir: Path) -> None:
    """Mirror datadirs to linkify_dir with URL-linkified .md files.

    For each datadir, a corresponding subdirectory is created under linkify_dir.
    Each visible data file is written as <filename>.md whose content is the
    original text wrapped in a single <pre> block with URLs converted to
    clickable <a> tags, suitable for rendering on GitHub.

    Supported layouts (no deeper nesting):
        - Flat: one datadir that is config_rootdir; files land in linkify_dir directly.
        - Subdir: multiple datadirs one level under config_rootdir; each maps to
          linkify_dir/<datadir_name>/.

    All existing content under linkify_dir is deleted before writing, so stale
    files and directories from previous runs are always removed.

    Args:
        datadirs: List of datadir paths.
        linkify_dir: Root of the mirror directory tree.
    """
    if linkify_dir.exists():
        shutil.rmtree(linkify_dir)
    linkify_dir.mkdir(parents=True)

    config_rootdir = datadirs[0] if len(datadirs) == 1 else datadirs[0].parent

    for datadir in datadirs:
        rel = datadir.relative_to(config_rootdir)
        mirror_dir = linkify_dir / rel
        mirror_dir.mkdir(parents=True, exist_ok=True)

        for datafile in sorted(datadir.iterdir()):
            if datafile.name.startswith(".") or not datafile.is_file():
                continue
            text = datafile.read_text(encoding="utf-8")
            md_content = _linkify_lines(text)
            (mirror_dir / (datafile.name + ".md")).write_text(md_content, encoding="utf-8")


def _linkify_lines(text: str) -> str:
    """Wrap text in <pre> and convert URLs into clickable HTML links."""
    linked_text = URL_RE.sub(_replace_url, text)
    return "<pre>\n" + linked_text.rstrip("\n") + "\n</pre>\n"


def _replace_url(match: re.Match) -> str:
    """Convert a detected URL into an HTML link while preserving punctuation."""
    url = match.group(1)
    punctuation = match.group(2)
    return f'<a href="{url}">{url}</a>' + punctuation
