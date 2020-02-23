"""Rule class and instantiation of rule objects from rule files."""

import csv
import os
import re
from pathlib import Path
from dataclasses import dataclass
from .config import (
    CONFIGFILE_NAME,
    DATADIR_RULEFILE_NAME,
    ROOTDIR_RULEFILE_NAME,
    VALID_FILENAME_CHARACTERS_REGEX,
)
from .exceptions import BadFilenameError, BadRegexError, RuleError, RulesError


@dataclass
class Rule:
    """Holds state, transforms, and self-validation methods for a single rule object."""

    source_matchfield: int = None
    source_matchpattern: str = None
    source: str = None
    target: str = None
    target_sortorder: int = None
    sources_list_is_initialized = False
    sources_list = []

    def coerce_types(self):
        """Coerces fields of data class to specific types (or exits with error)."""
        self._coerce_source_matchfield_as_integer()
        self._coerce_source_matchpattern_as_compiled_regex()
        self._coerce_source_as_valid_filename()
        self._coerce_target_as_valid_filename()
        self._coerce_target_sortorder_as_integer()
        return self

    def _coerce_source_matchfield_as_integer(self):
        """Coerces source_matchfield to be of type integer."""
        try:
            self.source_matchfield = abs(int(self.source_matchfield))
        except ValueError:
            print(self)
            raise RuleError(f"{repr(self.source_matchfield)} is not an integer.")
        return self

    def _coerce_source_matchpattern_as_compiled_regex(self):
        """Coerces source_matchpattern to be of type regex."""
        try:
            self.source_matchpattern = re.compile(self.source_matchpattern)
        except (re.error, TypeError):
            print(self)
            raise BadRegexError(f"{repr(self.source_matchpattern)} not valid as regex.")
        return self

    def _coerce_source_as_valid_filename(self):
        """Coerces source filename (or Path object) as valid filename string."""
        self.source = _get_validated_filename(self.source)
        return self

    def _coerce_target_as_valid_filename(self):
        """Coerces target filename (or Path object) as valid filename string."""
        self.target = _get_validated_filename(self.target)
        return self

    def _coerce_target_sortorder_as_integer(self):
        """Coerces target_sortorder to be of type integer."""
        try:
            self.target_sortorder = abs(int(self.target_sortorder))
        except ValueError:
            print(self)
            raise RuleError(f"{repr(self.target_sortorder)} is not an integer.")
        return self

    def is_valid(self):
        """Return True if Rule object passes all conversions and tests."""
        self._source_filename_field_is_not_equal_target()
        self._source_filename_field_was_properly_initialized()
        return True

    def _source_filename_field_was_properly_initialized(self):
        """Returns True if 'source' filename was initialized as a source."""
        if not Rule.sources_list_is_initialized:
            Rule.sources_list.append(self.source)
            Rule.sources_list_is_initialized = True
        if self.source not in Rule.sources_list:
            raise RuleError(f"{repr(self.source)} not initialized as 'source'.")
        if self.target not in Rule.sources_list:
            Rule.sources_list.append(self.target)
        return True

    def _source_filename_field_is_not_equal_target(self):
        """Returns True if source is not equal to target."""
        if self.source == self.target:
            raise RuleError("Source must not equal target.")
        return True


def get_rules(datadir=None):
    """Return list of Rule objects from one or more rule files."""
    if not datadir:
        datadir = Path.cwd()
    rulefile_chain = _find_rulefile_chain(datadir)
    rule_component_lists_aggregated = []
    for rulefile in rulefile_chain:
        rule_component_lists = _read_components_from_rulefile(rulefile)
        rule_component_lists_aggregated.extend(rule_component_lists)
    rules = _get_ruleobjs_from_components(rule_component_lists_aggregated)
    return rules


def _find_rulefile_chain(
    datadir=None,
    rootdir_rulefile=ROOTDIR_RULEFILE_NAME,
    datadir_rulefile=DATADIR_RULEFILE_NAME,
    configfile=CONFIGFILE_NAME,
):
    """Return list of rule files from root to specified data directory."""
    if not datadir:
        datadir = Path.cwd()
    os.chdir(datadir)
    subdir_chain_upwards = list(Path(datadir).parents)
    subdir_chain_upwards.insert(0, Path.cwd())
    rulefile_chain = []
    for subdir in subdir_chain_upwards:
        if datadir_rulefile in os.listdir(subdir):
            rulefile_chain.insert(0, subdir.joinpath(datadir_rulefile))
        if datadir_rulefile not in os.listdir(subdir):
            if configfile in os.listdir(subdir):
                rulefile_chain.insert(0, subdir.joinpath(rootdir_rulefile))
            else:
                break
    return rulefile_chain


def _read_components_from_rulefile(csvfile=None):
    """Return lists of lists, string items stripped, from pipe-delimited CSV file."""
    csv.register_dialect("rules", delimiter="|", quoting=csv.QUOTE_NONE)
    try:
        csvfile_obj = open(csvfile, newline="", encoding="utf-8")
    except FileNotFoundError:
        raise RulesError(f"Rule file not found.")
    except TypeError:
        raise RulesError(f"No rule file specified.")
    rule_component_list_raw = list(csv.reader(csvfile_obj, dialect="rules"))
    rule_component_list = []
    for single_rule_list in rule_component_list_raw:
        single_rule_list_depadded = []
        if len(single_rule_list) > 4:
            for item in single_rule_list:
                single_rule_list_depadded.append(item.strip())
        if single_rule_list_depadded:
            if single_rule_list_depadded[0].isdigit():
                rule_component_list.append(single_rule_list_depadded[0:5])
    return rule_component_list


def _get_ruleobjs_from_components(pyobj=None):
    """Return list of Rule objects from list of lists of rule components."""
    if not pyobj:
        raise RulesError("Expecting list of lists of rule components.")
    ruleobj_list = []
    for item in pyobj:
        try:
            if Rule(*item).is_valid():
                ruleobj_list.append(Rule(*item).coerce_types())
        except (ValueError, TypeError):
            raise RuleError(f"Rule {repr(item)} is badly formed.")
    return ruleobj_list


def _get_validated_filename(filename=None, valid_chars=VALID_FILENAME_CHARACTERS_REGEX):
    """Return filename, but only if it passes all sanity tests."""
    if filename is None:
        raise BadFilenameError(f"{repr(filename)} is not a valid filename.")
    if isinstance(filename, Path):
        if str(filename) == Path(filename).name:
            filename = Path(filename).name
    for char in filename:
        if not bool(re.search(valid_chars, char)):
            raise BadFilenameError(f"Filenames must use only {repr(valid_chars)}.")
    if Path(filename).is_dir():
        raise BadFilenameError(f"{repr(filename)} is name of existing directory.")
    if re.match(r"\.", filename):
        raise BadFilenameError(f"{repr(filename)} must not start with dot.")
    return filename
