"""Plan model objects are immutable by design."""

from pathlib import Path
import pytest
from mklists.plan.model import (
    DatadirPlan,
    PassPlan,
    SkippedDatadir,
    RunPlan,
)


@pytest.mark.parametrize(
    "instance",
    [
        DatadirPlan(
            datadir=Path("/tmp/datadira"),
            rules=[],
            rulefiles_used=[],
        ),
        PassPlan(
            snapshot_dir=Path("/tmp/backups/2026-03-01_123123123_01"),
            repo_configfile_found=None,
            repo_rulefile_found=None,
        ),
        SkippedDatadir(
            datadir=Path("/tmp/datadirb"),
            datadir_configfile_found=Path("/tmp/datadirb/.mklistsrc"),
        ),
        RunPlan(
            pass_plans=[],
            datadir_plans=[],
            skipped_datadirs=[],
            routing_dict={},
            htmldir=None,
        ),
    ],
)
def test_execution_contexts_are_immutable(instance):
    """Execution model objects are immutable by architectural design."""
    with pytest.raises((AttributeError, TypeError)):
        instance.__dict__  # will fail if slots=True

    with pytest.raises((AttributeError, TypeError)):
        setattr(instance, "new_field", 123)
