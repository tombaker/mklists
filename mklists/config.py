"""For initializing a new repo."""

import datetime
import os
from pathlib import Path
from warnings import warn
from .exceptions import MklistsError, ConfigWarning

# pylint: disable=anomalous-backslash-in-string
# => the slashes in "invalid filename patterns" are valid in YAML

BACKUPDIR_NAME = "_backups"
CONFIGFILE_NAME = "mklists.yml"
DATADIR_RULEFILE_NAME = ".rules"
HTMLDIR_NAME = "_html"
ROOTDIR_RULEFILE_NAME = "rules.cfg"
TIMESTAMP_STR = datetime.datetime.now().strftime("%Y-%m-%d_%H%M_%S%f")
URL_PATTERN_REGEX = r"""((?:git://|http://|https://|file:///)[^ <>'"{}(),|\\^`[\]]*)"""
VALID_FILENAME_CHARACTERS_REGEX = r"[\-_=.,@:A-Za-z0-9]+$"

CONFIGFILE_CONTENT = (
    "verbose: True\n"
    "backup_depth: 3\n"
    "linkify: True\n"
    "# \n"
    "invalid_filename_patterns:\n"
    "- \.swp$\n"
    "- \.tmp$\n"
    "- ~$\n"
    "# \n"
    "# # maps files to destinations (paths are absolute or relative to repo root)\n"
    "# files2dirs_dict:\n"
    "#     to_a.txt: a\n"
    "#     to_b.txt: b\n"
    "#     to_c.txt: /Users/foo/logs\n"
    "# \n"
    "# # lists stems of pathnames to be linkified\n"
    "# pathstem_list:\n"
    "# - /Users/foobar\n"
    "# - /home/foobar\n"
)

DATADIR_NAME = "lists"
DATADIR_DATAFILE_NAME = "README.txt"
DATADIR_DATAFILE_CONTENTS = (
    "NOW Examine 'a/.rules' file (in this directory); edit as needed.\n"
    "NOW Hint: Examine '.rules' file in root directory; leave unchanged for now..\n"
    "NOW Hint: Change beginning of this line to today's date (eg, 2020-01-17).\n"
    "NOW Hint: Then run 'mklists' to see what happens to these lines.\n"
    "NOW Change the name of this directory, as needed.\n"
    "NOW If you already understand 'mklists', replace these lines with your own.\n"
    "LATER Check out 'mklists.yml' in the root directory.\n"
    "LATER Hint: Create 'b' directory as a destination for 'log.txt'.\n"
)

ROOTDIR_RULEFILE_CONTENTS = (
    "# Global rules.\n"
    "in field|match |in source  |move to    |sort by|\n"
    "0       |.     |lines.tmp  |lines      |1      |Comments here.\n"
)
DATADIR_RULEFILE_MINIMAL_CONTENTS = "0|.|lines|todo.txt|0|Comments...\n"
DATADIR_RULEFILE_CONTENTS = (
    "# First five fields in lines that start with integers are parsed as rules.\n"
    "# Everything else - empty lines, comments, extra fields - is ignored.\n"
    "# For readability, fields may contain whitespace on the left or right.\n"
    "# 1. Field in source line to be matched.\n"
    "#    Value '0' means 'match anywhere in line'.\n"
    "# 2. Regex matched against the source field or line.\n"
    "#    Regex may contain spaces: '|   ^2020 ..  |' = regex '^2020 ..'.\n"
    "# 3. Source: in-memory set of lines _from_ which lines matching regex are moved.\n"
    "# 4. Target: in-memory set of lines _to_ which lines matching regex are moved.\n"
    "# 5. Field by which target is to be sorted.\n"
    "#    Value '0' means 'sort on entire line'.\n"
    "#    Absence of a value (blank field) means 'do not sort'.\n"
    "# At the end, non-empty sources and targets are written to files.\n"
    "\n"
    "in field|match |in source  |move to    |sort by|\n"
    "0       |.     |lines      |todo.txt   |1      |Comments here.\n"
    "1       |NOW   |todo.txt   |now.txt  |1      |Pipe delimiters need not align.\n"
    "1       |LATER |todo.txt   |later.txt  |       |'later.txt' will not be sorted.\n"
    "1       |^2020 |todo.txt   |log.txt    |0      |\n"
)


def write_minimal_rulefiles(
    rootdir_path=None,
    datadir_name=DATADIR_NAME,
    datadir_rulefile=DATADIR_RULEFILE_NAME,
    datadir_rulefile_contents=DATADIR_RULEFILE_MINIMAL_CONTENTS,
    root_rulefile=ROOTDIR_RULEFILE_NAME,
    root_rulefile_contents=ROOTDIR_RULEFILE_CONTENTS,
):
    """Write starter rule files to root directory and to starter data directory."""
    # pylint: disable=too-many-arguments
    if not rootdir_path:
        rootdir_path = Path.cwd()
    rootdir_rules = Path(root_rulefile)
    datadir = Path(rootdir_path) / datadir_name
    datadir.mkdir(parents=True, exist_ok=True)
    datadir_rules = Path(datadir) / datadir_rulefile
    if rootdir_rules.exists():
        warn(f"Will use existing rule file {str(rootdir_rules)}.", ConfigWarning)
    else:
        rootdir_rules.write_text(root_rulefile_contents)
    if datadir_rules.exists():
        warn(f"Will use existing rule file {str(datadir_rules)}.", ConfigWarning)
    else:
        datadir_rules.write_text(datadir_rulefile_contents)


def write_starter_configfile(
    rootdir_path=None,
    configfile_name=CONFIGFILE_NAME,
    configfile_content=CONFIGFILE_CONTENT,
):
    """Write initial config file (mklists.yml) to root directory."""
    if not rootdir_path:
        rootdir_path = Path.cwd()
    file_tobewritten_pathname = Path(rootdir_path) / configfile_name
    if os.path.exists(file_tobewritten_pathname):
        raise MklistsError(f"Repo already initialized.")
    with open(file_tobewritten_pathname, "w", encoding="utf-8") as outfile:
        outfile.write(configfile_content)


def write_starter_datafile(
    rootdir_path=None,
    datadir_name=DATADIR_NAME,
    datadir_datafile_name=DATADIR_DATAFILE_NAME,
    datadir_datafile_contents=DATADIR_DATAFILE_CONTENTS,
):
    """Write starter data file to data directory."""
    if not rootdir_path:
        rootdir_path = Path.cwd()
    datadir = Path(rootdir_path) / datadir_name
    datadir.mkdir(parents=True, exist_ok=True)
    Path(datadir).mkdir(parents=True, exist_ok=True)
    Path(datadir).joinpath(datadir_datafile_name).write_text(datadir_datafile_contents)


def write_starter_rulefiles(
    rootdir_path=None,
    datadir_name=DATADIR_NAME,
    datadir_rulefile=DATADIR_RULEFILE_NAME,
    datadir_rulefile_contents=DATADIR_RULEFILE_CONTENTS,
    root_rulefile=ROOTDIR_RULEFILE_NAME,
    root_rulefile_contents=ROOTDIR_RULEFILE_CONTENTS,
):
    """Write starter rule files to root directory and to starter data directory."""
    # pylint: disable=too-many-arguments
    if not rootdir_path:
        rootdir_path = Path.cwd()
    Path(root_rulefile).write_text(root_rulefile_contents)
    datadir = Path(rootdir_path) / datadir_name
    datadir.mkdir(parents=True, exist_ok=True)
    Path(datadir).joinpath(datadir_rulefile).write_text(datadir_rulefile_contents)
