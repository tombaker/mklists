"""Write contents of dictionary 'filenames2lines_dict' to disk files."""

import io
import os
import re
from pathlib import Path
from .apply import _get_visiblefile_paths, _find_rootdir_path
from .config import HTMLDIR_NAME, URL_PATTERN_REGEX
from .exceptions import BadFilenameError


def write_htmlfiles(filenames2lines_dict=None, datadir=None):
    """Writes contents of in-memory dictionary, urlified, to disk."""
    if not datadir:
        datadir = Path.cwd()
    htmldir_subdir_pathname = _get_htmldir_path()
    if not os.path.exists(htmldir_subdir_pathname):
        Path(htmldir_subdir_pathname).mkdir(parents=True, exist_ok=True)
    os.chdir(htmldir_subdir_pathname)
    for file in _get_visiblefile_paths():
        os.remove(file)
    for key in list(filenames2lines_dict.keys()):
        lines_to_be_written = []
        for line in filenames2lines_dict[key]:
            lines_to_be_written.append(_get_linkified_textline(line))
        file_to_write = key + ".html"
        io.open(file_to_write, "w", encoding="utf-8").writelines(lines_to_be_written)


def _get_htmldir_path(datadir=None, rootdir=None, htmldir_name=HTMLDIR_NAME):
    """Return pathname for folder holding htmlified data files."""
    if not rootdir:
        rootdir = _find_rootdir_path()
    if not datadir:
        datadir = Path.cwd()
    html_subdir = Path(datadir).relative_to(rootdir)
    try:
        htmldir_path = Path(rootdir).joinpath(htmldir_name, html_subdir)
    except TypeError:
        raise BadFilenameError(f"'htmldir_name' must be a valid directory name.")
    return htmldir_path


def _get_linkified_textline(line=None, url_regex=URL_PATTERN_REGEX):
    """Return text lines with URLs wrapped with HREF tags."""
    if "<a href=" in line or "<A HREF=" in line:
        return line
    return re.compile(url_regex).sub(r'<a href="\1">\1</a>', line.rstrip()) + "\n"
