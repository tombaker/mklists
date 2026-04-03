"""Tests that run_mklists logs datadir paths at INFO level."""

import logging
import re

import pytest

from mklists.config.model import SafetyConfig
from mklists.exec.run import run_mklists
from mklists.plan.model import DatadirPlan, PassPlan, RunPlan
from mklists.rules.load import load_rules_for_datadir


@pytest.fixture(autouse=True)
def clean_mklists_logger():
    """Remove all handlers from the mklists logger after each test."""
    yield
    lg = logging.getLogger("mklists")
    for handler in lg.handlers[:]:
        handler.close()
        lg.removeHandler(handler)


def make_run_plan(datadir_plan: DatadirPlan) -> RunPlan:
    """Build a minimal RunPlan containing one DatadirPlan."""
    return RunPlan(
        pass_plans=[PassPlan(snapshot_dir=None, snapshot_datatree_configfiles=[])],
        datadir_plans=[datadir_plan],
        skipped_datadirs=[],
        routing_dict={},
        linkify_md_dir=None,
        linkify_html_dir=None,
        is_datatree_root=True,
        safety=SafetyConfig(invalid_filename_patterns=[]),
        backup=None,
    )


def test_run_mklists_logs_datadir_path(tmp_path, caplog):
    """run_mklists logs the full path of each datadir at INFO level."""
    rulefile = tmp_path / ".rules"
    rulefile.write_text("0|.|input.txt|output.txt|\n")
    (tmp_path / "input.txt").write_text("hello\n")

    run_plan = make_run_plan(
        DatadirPlan(
            datadir=tmp_path,
            rules=load_rules_for_datadir([rulefile]),
            rulefiles_used=[rulefile],
        )
    )

    with caplog.at_level(logging.INFO, logger="mklists"):
        run_mklists(run_plan)

    assert str(tmp_path) in caplog.text


def test_run_mklists_logs_each_datadir_path(tmp_path, caplog):
    """run_mklists logs a path for each datadir in the plan."""
    dirs = [tmp_path / name for name in ("a", "b")]
    for d in dirs:
        d.mkdir()
        (d / ".rules").write_text("0|.|input.txt|output.txt|\n")
        (d / "input.txt").write_text("hello\n")

    run_plan = RunPlan(
        pass_plans=[PassPlan(snapshot_dir=None, snapshot_datatree_configfiles=[])],
        datadir_plans=[
            DatadirPlan(
                datadir=d,
                rules=load_rules_for_datadir([d / ".rules"]),
                rulefiles_used=[d / ".rules"],
            )
            for d in dirs
        ],
        skipped_datadirs=[],
        routing_dict={},
        linkify_md_dir=None,
        linkify_html_dir=None,
        is_datatree_root=True,
        safety=SafetyConfig(invalid_filename_patterns=[re.compile(r"\.swp$")]),
        backup=None,
    )

    with caplog.at_level(logging.INFO, logger="mklists"):
        run_mklists(run_plan)

    for d in dirs:
        assert str(d) in caplog.text
