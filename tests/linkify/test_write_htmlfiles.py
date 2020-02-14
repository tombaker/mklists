"""Write contents of filename-to-datalines dictionary to files as named."""

import os
from pathlib import Path
from mklists.config import HTMLDIR_NAME, CONFIGFILE_NAME
from mklists.linkify import write_htmlfiles

DATADICT_BEFORE = {
    "filea.txt": ["DC2019 http://dublincore.org/confs/2019\n", "DC2019 Sep 23-26\n"],
    "fileb.txt": [
        "SHEX Primer: http://shex.io/shex-primer\n",
        "SHEX Wikidata: http://bit.ly/foobar\n",
    ],
}

TEST_FILEA_HTMLSTR = """\
DC2019 <a href="http://dublincore.org/confs/2019">http://dublincore.org/confs/2019</a>
DC2019 Sep 23-26
"""

TEST_FILEB_HTMLSTR = """\
SHEX Primer: <a href="http://shex.io/shex-primer">http://shex.io/shex-primer</a>
SHEX Wikidata: <a href="http://bit.ly/foobar">http://bit.ly/foobar</a>
"""


def test_write_filenames2lines_dict_to_html_files(tmp_path):
    """Writes datalines to HTML files in HTML directory."""
    os.chdir(tmp_path)
    Path(tmp_path).joinpath(CONFIGFILE_NAME).write_text("config stuff")
    htmlsub = Path(tmp_path).joinpath(HTMLDIR_NAME, "a")
    htmlsub.mkdir(parents=True, exist_ok=True)
    datadir = Path(tmp_path).joinpath("a")
    datadir.mkdir()
    Path(datadir).joinpath("filea.txt").write_text("some text")
    Path(datadir).joinpath("fileb.txt").write_text("some text")
    os.chdir(datadir)
    write_htmlfiles(filenames2lines_dict=DATADICT_BEFORE)
    assert Path(htmlsub).joinpath("filea.txt.html").read_text() == TEST_FILEA_HTMLSTR
    assert Path(htmlsub).joinpath("fileb.txt.html").read_text() == TEST_FILEB_HTMLSTR


def test_write_html_files_after_clearing_directory(tmp_path):
    """Deletes existing files in HTML directory before writing datalines."""
    os.chdir(tmp_path)
    Path(tmp_path).joinpath(CONFIGFILE_NAME).write_text("config stuff")
    htmlsub = Path(tmp_path).joinpath(HTMLDIR_NAME, "a")
    htmlsub.mkdir(parents=True, exist_ok=True)
    Path(htmlsub).joinpath("some_file.txt.html").write_text("<p>some HTML content</p>")
    datadir = Path(tmp_path).joinpath("a")
    datadir.mkdir()
    Path(datadir).joinpath("filea.txt").write_text("some text")
    Path(datadir).joinpath("fileb.txt").write_text("some text")
    os.chdir(datadir)
    write_htmlfiles(filenames2lines_dict=DATADICT_BEFORE)
    assert Path(htmlsub).joinpath("filea.txt.html").read_text() == TEST_FILEA_HTMLSTR
    assert Path(htmlsub).joinpath("fileb.txt.html").read_text() == TEST_FILEB_HTMLSTR
    assert not os.path.exists("some_file.txt.html")


def test_write_htmlfiles_creates_htmldir_if_not_exist(tmp_path):
    """Creates HTML directory before writing datalines."""
    Path(tmp_path).joinpath(CONFIGFILE_NAME).write_text("config stuff")
    # Emulates output of get_htmldir_path() but does not create directory:
    htmlsub = Path(tmp_path).joinpath(HTMLDIR_NAME, "a")
    datadir = Path(tmp_path).joinpath("a")
    datadir.mkdir()
    Path(datadir).joinpath("filea.txt").write_text("some text")
    Path(datadir).joinpath("fileb.txt").write_text("some text")
    os.chdir(datadir)
    write_htmlfiles(filenames2lines_dict=DATADICT_BEFORE)
    assert Path(htmlsub).joinpath("filea.txt.html").read_text() == TEST_FILEA_HTMLSTR
    assert Path(htmlsub).joinpath("fileb.txt.html").read_text() == TEST_FILEB_HTMLSTR
