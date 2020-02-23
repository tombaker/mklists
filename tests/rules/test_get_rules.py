"""Return list of rule objects from rule files."""

import os
import re
import pytest
from pathlib import Path
from mklists.config import CONFIGFILE_NAME, DATADIR_RULEFILE_NAME, ROOTDIR_RULEFILE_NAME
from mklists.rules import (
    Rule,
    get_rules,
    _read_components_from_rulefile,
    _find_rulefile_chain,
)

# pylint: disable=unused-argument
# In tests, fixture arguments may look like they are unused.

ROOTDIR_RULESTR = "0|.|x|lines|0|A comment\n"
DIRA_RULESTR = "1|NOW|lines|alines|1|Another comment\n" "1|LATER|lines|alines|1|\n"
DIRB_RULESTR = "0|^2019 ..|lines|blines|1|\n"
RULEOBJ_LIST = [
    Rule(
        source_matchfield=0,
        source_matchpattern=re.compile("."),
        source="x",
        target="lines",
        target_sortorder=0,
    ),
    Rule(
        source_matchfield=1,
        source_matchpattern=re.compile("NOW"),
        source="lines",
        target="alines",
        target_sortorder=1,
    ),
    Rule(
        source_matchfield=1,
        source_matchpattern=re.compile("LATER"),
        source="lines",
        target="alines",
        target_sortorder=1,
    ),
    Rule(
        source_matchfield=0,
        source_matchpattern=re.compile("^2019 .."),
        source="lines",
        target="blines",
        target_sortorder=1,
    ),
]


def test_get_rules(tmp_path):
    """@@@Docstring."""
    os.chdir(tmp_path)
    Path(tmp_path).joinpath(CONFIGFILE_NAME).write_text("config stuff")
    rulefile0 = Path(tmp_path).joinpath(ROOTDIR_RULEFILE_NAME)
    rulefile0.write_text(ROOTDIR_RULESTR)
    ab = Path(tmp_path).joinpath("a/b")
    ab.mkdir(parents=True, exist_ok=True)
    rulefile1 = Path(tmp_path).joinpath("a", DATADIR_RULEFILE_NAME)
    rulefile1.write_text(DIRA_RULESTR)
    rulefile2 = Path(tmp_path).joinpath("a/b", DATADIR_RULEFILE_NAME)
    rulefile2.write_text(DIRB_RULESTR)
    os.chdir(ab)
    rulefile_chain = _find_rulefile_chain()
    assert rulefile_chain == [rulefile0, rulefile1, rulefile2]
    expected = RULEOBJ_LIST
    real = get_rules()
    assert real == expected


def test_read_components_from_rulefile_rulefile_not_specified(tmp_path):
    """Raises NoRulefileError if @@@."""
    with pytest.raises(SystemExit):
        _read_components_from_rulefile(csvfile=None)
