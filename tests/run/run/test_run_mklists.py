"""Testing `run.run_mklists`

`run_mklists` does almost nothing (and returns None):
- Everything important happens because of it.

No need to test:
- results returned (because collaborators are already well-tested)
- filesystem
- real configs
- real passes

Test only whether it coordinates its collaborators correctly:
- what it calls, with what arguments, how often
- not an integration test: testing control flow

Assert:
- run completes without error
- expected directories and files are created
- both passes ran

How:
- do not use filesystem
- do not use real configs
- use minimal stub RunPlan
- monkeypatch collaborators
- assert calls and call counts

Principles:
- A run processes all discovered datadirs.
- Each datadir has an effective configfile.
- Config objects are loaded per unique configfile and applied per datadir.
"""

from pathlib import Path
import pytest
from mklists.config import SettingsContext
from mklists.run.run import run_mklists
from mklists.structure.contexts_datadir import DatadirContext
from mklists.plan import RunPlan, PassPlan


def test_run_mklists_loads_config_per_unique_configfile(monkeypatch):
    """Function `load_config` is called once per unique `configfile_used`."""
    repo_cfg = Path("/repo/mklists.yaml")

    datadir_contexts = [
        DatadirContext(datadir=Path("/repo/a"), configfile_used=repo_cfg, rules=[]),
        DatadirContext(datadir=Path("/repo/b"), configfile_used=repo_cfg, rules=[]),
    ]

    run_plan = RunPlan(
        datadir_contexts=datadir_contexts,
        pass_plans=[PassPlan(backup_snapshot_dir=None)],
        repo_configfile=None,
        repo_rulefile=None,
        backup_rootdir=None,
        backup_depth=None,
        routing_dict={},
        htmldir=None,
    )

    calls: list[Path | None] = []

    # The real `load_config` returns a SettingsContext object that can be passed
    # to `process_datadir`.
    # But we are not testing SettingsContext here: `fake_load_config` can return a
    # trivial, fake object because that object is never inspected (see below).
    def fake_load_config(configfile_used: Path | None):
        calls.append(configfile_used)
        return object()

    import mklists.run.run as execute_module

    monkeypatch.setattr(
        target=execute_module, 
        name="load_config", 
        value=fake_load_config,
        raising=True,
    )

    # `lambda **kwargs: None` ensures that `mklists_cfg` is never inspected.
    monkeypatch.setattr(
        target=execute_module, 
        name="process_datadir", 
        value=lambda **kwargs: None,
        raising=True,
    )

    execute_module.run_mklists(run_plan)

    # This will pass if caching logic is implemented:
    assert calls == [repo_cfg]
