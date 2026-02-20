"""Testing `run.run_mklists`

`run_mklists` does almost nothing (and returns None):
- Everything important happens because of it.

No need to test:
- results returned (because collaborators are already well-tested)
- filesystem
- real configs
- real passes

Test only whether it coordinates its collaborators correctly:
- what it calls, with what arguments, how often:
  - 1 x load_config(config_rootdir)
  - 1 x _find_datadirs
  - 1 x _make_timestamp
  - 2 x run_pass
- not an integration test: testing control flow

Assert:
- run completes without error
- expected directories and files are created
- both passes ran

How:
- use temporary directory
- provide minimal real config
- create dummy datadirs
- let run_pass run against harmless fixtures
"""

import pytest
from mklists.execute import run_mklists


@pytest.mark.skip
def test_run_mklists_shallow(tmp_path, capsys):
    """Shallow integration test:
    - real filesystem
    - real config
    - real datadirs
    - no deep assertions
    """
    repo_dir = tmp_path / "mklists"
    repo_dir.mkdir()
    (repo_dir / "mklists.yaml").write_text(
        """
        backup:
          backup_enabled: True
          backup_dir: backups
          backup_depth: 3
        """
    )

    datadir1 = repo_dir / "datadir1"
    datadir2 = repo_dir / "datadir2"
    for datadir in (datadir1, datadir2):
        datadir.mkdir()
        (datadir / "input.txt").write_text("dummy data file")
        (datadir / ".rules").write_text("0|.|input|output|")

    run_mklists(config_rootdir=repo_dir)

    assert (repo_dir / "backups").exists()
