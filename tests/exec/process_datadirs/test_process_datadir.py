"""Tests $MKLMKL/exec/process_datadirs.py"""

import re
import pytest
from mklists.config.model import SafetyConfig
from mklists.exec.process_datadirs import process_datadir
from mklists.plan.model import DatadirPlan
from mklists.rules.model import Rule


_SAFETY = SafetyConfig(invalid_filename_patterns=[])


def _rule(source, target, pattern=".", field=0, sortkey=None):
    return Rule(
        source_matchfield=field,
        source_matchpattern=re.compile(pattern),
        source=source,
        target=target,
        target_sortkey=sortkey,
    )


# ---------------------------------------------------------------------------
# Basic pipeline behaviour
# ---------------------------------------------------------------------------


def test_process_datadir_writes_output_file(tmp_path):
    """Lines from input file are dispatched and written to output file."""
    (tmp_path / "input.txt").write_text("alpha\nbeta\n")

    plan = DatadirPlan(
        datadir=tmp_path,
        rules=[_rule("input.txt", "output.txt")],
        rulefiles_used=[],
    )

    process_datadir(datadir_plan=plan, safety=_SAFETY)

    assert (tmp_path / "output.txt").read_text() == "alpha\nbeta\n"


def test_process_datadir_deletes_input_file(tmp_path):
    """Input file is deleted after lines are dispatched."""
    (tmp_path / "input.txt").write_text("alpha\nbeta\n")

    plan = DatadirPlan(
        datadir=tmp_path,
        rules=[_rule("input.txt", "output.txt")],
        rulefiles_used=[],
    )

    process_datadir(datadir_plan=plan, safety=_SAFETY)

    assert not (tmp_path / "input.txt").exists()


def test_process_datadir_unmatched_lines_stay_in_source(tmp_path):
    """Lines that do not match the rule pattern remain in the source file."""
    (tmp_path / "input.txt").write_text("KEEP this\nMOVE this\n")

    plan = DatadirPlan(
        datadir=tmp_path,
        rules=[_rule("input.txt", "output.txt", pattern="MOVE")],
        rulefiles_used=[],
    )

    process_datadir(datadir_plan=plan, safety=_SAFETY)

    assert (tmp_path / "input.txt").read_text() == "KEEP this\n"
    assert (tmp_path / "output.txt").read_text() == "MOVE this\n"


def test_process_datadir_hidden_files_not_deleted(tmp_path):
    """Hidden files such as .rules are not deleted during processing."""
    (tmp_path / ".rules").write_text("rules content\n")
    (tmp_path / "input.txt").write_text("data\n")

    plan = DatadirPlan(
        datadir=tmp_path,
        rules=[_rule("input.txt", "output.txt")],
        rulefiles_used=[],
    )

    process_datadir(datadir_plan=plan, safety=_SAFETY)

    assert (tmp_path / ".rules").read_text() == "rules content\n"


# ---------------------------------------------------------------------------
# Safety check integration
# ---------------------------------------------------------------------------


def test_process_datadir_raises_on_blank_line(tmp_path):
    """Safety check raises ValueError before dispatching if a file has a blank line."""
    (tmp_path / "input.txt").write_text("alpha\n\nbeta\n")

    plan = DatadirPlan(
        datadir=tmp_path,
        rules=[_rule("input.txt", "output.txt")],
        rulefiles_used=[],
    )

    with pytest.raises(ValueError):
        process_datadir(datadir_plan=plan, safety=_SAFETY)


def test_process_datadir_raises_on_invalid_filename(tmp_path):
    """Safety check raises ValueError if a filename matches a forbidden pattern."""
    (tmp_path / "bad~file.txt").write_text("data\n")

    plan = DatadirPlan(
        datadir=tmp_path,
        rules=[_rule("bad~file.txt", "output.txt")],
        rulefiles_used=[],
    )
    safety = SafetyConfig(invalid_filename_patterns=[re.compile(r"~")])

    with pytest.raises(ValueError):
        process_datadir(datadir_plan=plan, safety=safety)
