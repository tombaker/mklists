"""Load and validate transformation rules for a given data directory."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Pattern


DATADIR_CONFIGFILE_NAME = ".mklistsrc"  # @@@ SHOULD NOT BE NECESSARY


REPO_RULEFILE_NAME = "mklists.rules"
DATADIR_RULEFILE_NAME = ".rules"
FIELD_COUNT = 5
PIPE = "|"


@dataclass(frozen=True)
class Rule:
    """Immutable data structure for one validated rule."""

    source_matchfield: int
    source_matchpattern: Pattern[str]
    source: str
    target: str
    target_sortkey: int | None


class RuleError(ValueError):
    """Rule does not parse or validate."""


class FilenameError(RuleError):
    """Rule field is not valid as the name of a data file."""


def load_rules_for_datadir(rulefiles: list[Path]) -> list[Rule]:
    """Load effective rules for a data directory.

    Args:
        datadir: Path to data directory.

    Returns:
        List of rules (Rule objects).

    Raises:
        FileNotFoundError: If `.rules` not found in datadir.

    Note:
        Files are processed in given list order.
    """

    all_rules: list[Rule] = []

    for rulefile in rulefiles:
        if not rulefile.is_file():
            raise FileNotFoundError(rulefile)

        rules = _load_rules_from_rulefile(rulefile)
        all_rules.extend(rules)

    _validate_rulechain(all_rules)

    return all_rules


def _compile_pattern(text: str) -> Pattern[str]:
    """Successfully compile regex pattern.

    Args:
        text: Text of regular expression to be compiled.

    Returns:
        Compiled regular expression.

    Raises:
        RuleError: Regular expression text does not correctly compile.

    """
    try:
        return re.compile(text)
    except re.error as e:
        raise RuleError(f"Invalid regex {text!r}") from e


def _iter_rulelines(rulefile: Path) -> Iterable[str]:
    """Yield non-blank, non-comment lines in rule file with leading whitespace stripped.

    Args:
        rulefile: Pathname of rule file.

    Yields:
        Non-blank, non-comment lines, with whitespace stripped, from rule file.
    """
    for raw in rulefile.read_text().splitlines():
        line = raw.lstrip()
        if not line or line.startswith("#"):
            continue
        yield line


def _load_rules_from_rulefile(rulefile: Path) -> list[Rule]:
    """Load, parse, validate rules from a rule file.

    Args:
        rulefile: Path object for rule file.

    Returns:
        List of Rule objects.

    Note:
        Validation of rule lists is handled by another function.
    """
    rules: list[Rule] = []

    for line in _iter_rulelines(rulefile):
        ruleline_fields = _split_ruleline_into_fields(line)
        rule = _parse_rule(ruleline_fields)
        rules.append(rule)

    return rules


def _parse_rule(ruleline_fields: list[str]) -> Rule:
    """Convert list of raw rule line fields into validated Rule object.

    Args:
        ruleline_fields: List of fields extracted from one raw rule line.

    Returns:
        Rule object initialized with normalized rule line components.

    Raises:
        RuleError: Rule is invalid.

    Note:
        Semantics of fields in a raw rule line (1-based, as written in rule file):

        1. Source match field:
           Integer specifying which field of input line is tested against
           regex in field 2.

        2. Match pattern:
           Regular expression applied to text in source match field.

        3. Source list:
           Name of list from which matching lines are removed.

        4. Target list:
           Name of list to which matching lines are appended.

        5. Target sort field:
           Integer specifying which field of target line is used for sorting.
    """
    (raw_matchfield, raw_pattern, raw_source, raw_target, raw_sortorder) = (
        ruleline_fields
    )
    if not all(
        value.strip() for value in (raw_matchfield, raw_pattern, raw_source, raw_target)
    ):
        raise RuleError("Required rule fields must not be empty.")

    try:
        source_matchfield = int(raw_matchfield)
    except ValueError as e:
        raise RuleError("Source matchfield must be an integer.") from e

    if source_matchfield < 0:
        raise RuleError("Source match field must be zero or greater.")

    if raw_sortorder.strip() == "":
        target_sortkey = None
    else:
        try:
            target_sortkey = int(raw_sortorder)
        except ValueError as e:
            raise RuleError("Target sort order must be an integer if specified.") from e

        if target_sortkey < 0:
            raise RuleError("Target sort field must be a positive integer.")

    source_matchpattern = _compile_pattern(raw_pattern)
    source = raw_source.strip()
    target = raw_target.strip()

    if source == target:
        raise RuleError("Source and target must differ.")

    # Filenames must by default be plain ASCII with no spaces; this is configurable.
    _validate_filename(source)
    _validate_filename(target)

    return Rule(
        source_matchfield=source_matchfield,
        source_matchpattern=source_matchpattern,
        source=source,
        target=target,
        target_sortkey=target_sortkey,
    )


def _split_ruleline_into_fields(rule_line: str) -> list[str]:
    """Split single rule line into fields.

    Args:
        rule_line: Raw text line from rule file.

    Returns:
        Parsed list of rule-line components.

    Raises:
        RuleError: If line does not split into specified number of fields.
    """
    ruleline_fields = rule_line.split(PIPE)
    if len(ruleline_fields) != FIELD_COUNT:
        raise RuleError(
            f"Expected {FIELD_COUNT} fields, got {len(ruleline_fields)}: {rule_line!r}"
        )
    return ruleline_fields


def _validate_filename(filename: str) -> None:
    """Validate string for safe use as filename.

    Args:
        filename: String to be validated against strict rules for valid filenames.

    Returns:
        None, unless validation rules raise an exception on the given filename.

    Raises:
        FilenameError: Filename does not meet specific validation requirements.

    Note:
        Filenames must:
        - be strings
        - be non-empty
        - contain at least one alphanumeric character
        - not start with a dot
    """
    if not filename:
        raise FilenameError("Filename must not be empty.")

    if not re.search(r"\w", filename, re.UNICODE):
        raise FilenameError(
            "Filename must contain at least one alphanumeric character."
        )

    if "/" in filename:
        raise FilenameError("Filename must not contain path separators ('/').")

    if filename.startswith("."):
        raise FilenameError("Filename must not start with a dot.")


def _validate_rulechain(rules: list[Rule]) -> None:
    """Validate chain of Rule objects.

    Args:
        rules: Chain (list) of Rule objects.

    Returns:
        None, after possibly raising exceptions.

    Note:
        In a valid rule chain, every rule after the first must have a source whose
        name has appeared previously as either a source or a target.
        A rule that is valid in isolation may be invalid in the context of a sequence
        of multiple rules.
    """
    if not rules:
        return

    listnames_seen: set[str] = set()
    listnames_seen.add(rules[0].source)
    listnames_seen.add(rules[0].target)

    for rule in rules[1:]:
        if rule.source not in listnames_seen:
            raise RuleError(f"Source not previously seen: {rule.source!r}")
        listnames_seen.add(rule.target)
