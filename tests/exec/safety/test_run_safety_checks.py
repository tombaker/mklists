"""Edit $MKLMKL/exec/safety.py"""

import re
import pytest
from mklists.config import SafetyConfig
from mklists.exec.safety import run_safety_checks


@pytest.fixture
def safety_config():
    return SafetyConfig(
        invalid_filename_patterns=[
            re.compile(r"\.swp$"),
            re.compile(r"\.tmp$"),
            re.compile(r"\.vim$"),
            re.compile(r"~$"),
        ],
    )


def test_run_safety_checks_passes(tmp_path, safety_config):
    (tmp_path / "a.txt").write_text("alpha\nbeta\n")
    (tmp_path / "b.txt").write_text("one\ntwo\n")

    run_safety_checks(tmp_path, safety_config)


def test_run_safety_checks_stops_on_violation(tmp_path, safety_config):
    (tmp_path / "ok.txt").write_text("alpha\nbeta\n")
    (tmp_path / "bad.swp").write_text("junk\n")

    with pytest.raises(ValueError):
        run_safety_checks(tmp_path, safety_config)
