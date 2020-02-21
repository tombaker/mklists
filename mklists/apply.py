"""Core functions of mklists."""

import os
import re
import shutil
from pathlib import Path
from collections import defaultdict
import ruamel.yaml
from .config import CONFIGFILE_NAME, DATADIR_RULEFILE_NAME
from .exceptions import (
    BadFilenameError,
    BadYamlError,
    MklistsError,
    NotUTF8Error,
    DataError,
    RulesError,
)

# pylint: disable=bad-continuation
# Black disagrees.


def apply_rules_to_datalines(rules=None, datalines=None):
    """Returns filename-to-lines dictionary after applying rules to datalines."""
    if not rules:
        raise RulesError("No rules specified.")
    if not datalines:
        raise DataError("No data specified.")
    datadict = defaultdict(list)
    first_key_is_initialized = False
    for ruleobj in rules:
        if not first_key_is_initialized:
            datadict[ruleobj.source] = datalines
            first_key_is_initialized = True

        for line in datadict[ruleobj.source]:
            if _dataline_matches_ruleobj(ruleobj, line):
                datadict[ruleobj.target].append(line)
                datadict[ruleobj.source].remove(line)

        # Sort 'ruleobj.target' lines by field if sortorder was specified.
        if ruleobj.target_sortorder:
            eth_sortorder = ruleobj.target_sortorder - 1
            decorated = [
                (line.split()[eth_sortorder], __, line)
                for (__, line) in enumerate(datadict[ruleobj.target])
            ]
            decorated.sort()
            datadict[ruleobj.target] = [line for (___, __, line) in decorated]

    filenames2lines_dict = dict(datadict)
    return filenames2lines_dict


def _dataline_matches_ruleobj(ruleobj=None, dataline_str=None):
    """Returns True if data line matches pattern specified in given rule."""
    # Line does not match if given field greater than number of fields in line.
    if ruleobj.source_matchfield > len(dataline_str.split()):
        return False

    # Line matches if given field is zero and pattern is found anywhere in line.
    if ruleobj.source_matchfield == 0:
        if re.search(ruleobj.source_matchpattern, dataline_str):
            return True

    # Line matches if pattern is found in given field.
    if ruleobj.source_matchfield > 0:
        eth = ruleobj.source_matchfield - 1
        if re.search(ruleobj.source_matchpattern, dataline_str.split()[eth]):
            return True
    return False


def get_configdict(rootdir_path=None, configfile_name=CONFIGFILE_NAME):
    """Returns configuration dictionary from YAML config file (or exits with errors."""
    if not rootdir_path:
        rootdir_path = _get_rootdir_path()
    configfile = Path(rootdir_path) / configfile_name
    try:
        configfile_contents = Path(configfile).read_text()
    except FileNotFoundError:
        raise MklistsError(f"Config file {repr(configfile)} not found.")
    try:
        return ruamel.yaml.safe_load(configfile_contents)
    except ruamel.yaml.YAMLError:
        raise BadYamlError(f"Badly formatted YAML content.")


def get_datadir_paths_below(
    datadir=None,
    configfile_name=CONFIGFILE_NAME,
    datadir_rulefile_name=DATADIR_RULEFILE_NAME,
):
    """Return list of data directories below given directory."""
    if not datadir:
        datadir = Path.cwd()
    datadir_paths = []
    for dirpath, dirs, files in os.walk(datadir):
        dirs[:] = [d for d in dirs if not d[0] == "."]
        if datadir_rulefile_name in files:
            if configfile_name not in files:
                datadir_paths.append(Path(dirpath))
    return datadir_paths


def get_datalines(datadir=None, bad_filename_patterns=None):
    """Returns lines from files in current directory (or exits with errors)."""
    if not datadir:
        datadir = Path.cwd()
    visiblefiles_list = _get_visiblefile_paths(datadir)
    all_datalines = []
    for datafile in visiblefiles_list:
        try:
            datafile_lines = open(datafile).readlines()
        except UnicodeDecodeError:
            raise NotUTF8Error(f"{repr(datafile)} is not UTF8-encoded.")
        if bad_filename_patterns:
            for badpat in bad_filename_patterns:
                if re.search(badpat, datafile):
                    raise BadFilenameError(f"{repr(datafile)} matches {repr(badpat)}.")
        for line in datafile_lines:
            if not line.rstrip():
                raise DataError(f"{repr(datafile)} must have no blank lines.")
        all_datalines.extend(datafile_lines)
    if not all_datalines:
        raise DataError("No data to process!")
    return all_datalines


def _get_rootdir_path(datadir=None, configfile=CONFIGFILE_NAME):
    """Return root pathname of mklists repo wherever executed in repo."""
    if not datadir:
        datadir = Path.cwd()
    parents = list(Path(datadir).parents)
    parents.insert(0, Path.cwd())
    for directory in parents:
        if configfile in [item.name for item in directory.glob("*")]:
            return Path(directory)
    raise MklistsError(f"{repr(configfile)} not found - not a repo.")


def _get_visiblefile_paths(datadir=None):
    """Return list of pathnames of visible files (if all filenames are valid)."""
    if not datadir:
        datadir = Path.cwd()
    visiblefile_paths = []
    all_fns = [str(p) for p in Path(datadir).glob("*") if os.path.isfile(p)]
    all_fns_minus_dotfiles = [f for f in all_fns if not re.match(r"\.", Path(f).name)]
    if all_fns_minus_dotfiles:
        for fn in all_fns_minus_dotfiles:
            visiblefile_paths.append(fn)
    return sorted(visiblefile_paths)


def move_specified_datafiles_elsewhere(files2dirs_dict=None, rootdir_path=None):
    """Moves data files to specified destination directories."""
    for key in files2dirs_dict:
        destination_dir = Path(rootdir_path) / files2dirs_dict[key]
        if os.path.exists(key):
            if os.path.exists(destination_dir):
                shutil.move(key, destination_dir)


def write_new_datafiles(filenames2lines_dict=None):
    """Writes contents of file2lines dictionary to disk files."""
    for (key, value) in filenames2lines_dict.items():
        if value:
            with open(key, "w", encoding="utf-8") as fout:
                fout.writelines(value)
