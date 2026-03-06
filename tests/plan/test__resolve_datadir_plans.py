"""Tests for _resolve_datadir_plans."""

from pathlib import Path
from mklists.structure.markers import DATADIR_CONFIGFILE_NAME, DATADIR_RULEFILE_NAME
from mklists.structure.model import (
    DatadirStructuralContext,
    StartdirStructuralContext,
    StructuralContext,
)
from mklists.plan.model import DatadirPlan, SkippedDatadir
from mklists.plan.resolve import _resolve_datadir_plans


def make_structural_context(
    startdir: Path,
    *,
    repo_rulefile_found: Path | None = None,
    datadir_contexts: list[DatadirStructuralContext] | None = None,
) -> StructuralContext:
    """Build a StructuralContext for testing _resolve_datadir_plans.

    Note:
        Sets repo_configfile_found so that is_repo_root=True and
        config_rootdir=startdir, avoiding StructureError from the
        config_rootdir property.
    """
    return StructuralContext(
        startdir_context=StartdirStructuralContext(
            startdir=startdir,
            repo_configfile_found=startdir / "mklists.yaml",
            repo_rulefile_found=repo_rulefile_found,
            datadir_configfile_found=None,
            datadir_rulefile_found=None,
        ),
        datadir_contexts=datadir_contexts or [],
    )


# ----- normal datadirs (no configfile_found) ---------------------------------


def test_normal_datadir_without_repo_rulefile_creates_plan(tmp_path):
    """Normal datadir with no repo rulefile → DatadirPlan with only the datadir rulefile."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    ctx = make_structural_context(
        startdir=tmp_path,
        datadir_contexts=[
            DatadirStructuralContext(
                datadir=datadir,
                datadir_configfile_found=None,
                datadir_rulefile=rulefile,
            )
        ],
    )
    plans, skipped = _resolve_datadir_plans(structural_context=ctx)

    assert skipped == []
    assert len(plans) == 1
    assert plans[0].datadir == datadir
    assert plans[0].rulefiles_used == [rulefile]
    assert plans[0].rules == []


def test_normal_datadir_with_repo_rulefile_puts_it_first(tmp_path):
    """Repo rulefile is prepended to rulefiles_used before the datadir rulefile."""
    repo_rulefile = tmp_path / DATADIR_RULEFILE_NAME
    repo_rulefile.touch()
    datadir = tmp_path / "data"
    datadir.mkdir()
    datadir_rulefile = datadir / DATADIR_RULEFILE_NAME
    datadir_rulefile.touch()

    ctx = make_structural_context(
        startdir=tmp_path,
        repo_rulefile_found=repo_rulefile,
        datadir_contexts=[
            DatadirStructuralContext(
                datadir=datadir,
                datadir_configfile_found=None,
                datadir_rulefile=datadir_rulefile,
            )
        ],
    )
    plans, skipped = _resolve_datadir_plans(structural_context=ctx)

    assert skipped == []
    assert len(plans) == 1
    assert plans[0].rulefiles_used == [repo_rulefile, datadir_rulefile]


# ----- self-contained datadirs (configfile_found set) ------------------------


def test_selfcontained_datadir_goes_to_skipped_not_plans(tmp_path):
    """Datadir with configfile_found → SkippedDatadir, not DatadirPlan."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    configfile = datadir / DATADIR_CONFIGFILE_NAME
    configfile.touch()
    rulefile = datadir / DATADIR_RULEFILE_NAME
    rulefile.touch()

    ctx = make_structural_context(
        startdir=tmp_path,
        datadir_contexts=[
            DatadirStructuralContext(
                datadir=datadir,
                datadir_configfile_found=configfile,
                datadir_rulefile=rulefile,
            )
        ],
    )
    plans, skipped = _resolve_datadir_plans(structural_context=ctx)

    assert plans == []
    assert skipped == [SkippedDatadir(datadir=datadir, datadir_configfile_found=configfile)]


# ----- mixed datadirs --------------------------------------------------------


def test_mixed_normal_and_selfcontained_partitioned_correctly(tmp_path):
    """Normal datadir goes to plans; self-contained datadir goes to skipped."""
    normal_dir = tmp_path / "normal"
    normal_dir.mkdir()
    normal_rulefile = normal_dir / DATADIR_RULEFILE_NAME
    normal_rulefile.touch()

    self_dir = tmp_path / "self"
    self_dir.mkdir()
    self_configfile = self_dir / DATADIR_CONFIGFILE_NAME
    self_configfile.touch()
    self_rulefile = self_dir / DATADIR_RULEFILE_NAME
    self_rulefile.touch()

    ctx = make_structural_context(
        startdir=tmp_path,
        datadir_contexts=[
            DatadirStructuralContext(
                datadir=normal_dir,
                datadir_configfile_found=None,
                datadir_rulefile=normal_rulefile,
            ),
            DatadirStructuralContext(
                datadir=self_dir,
                datadir_configfile_found=self_configfile,
                datadir_rulefile=self_rulefile,
            ),
        ],
    )
    plans, skipped = _resolve_datadir_plans(structural_context=ctx)

    assert len(plans) == 1
    assert plans[0].datadir == normal_dir
    assert len(skipped) == 1
    assert skipped[0].datadir == self_dir
