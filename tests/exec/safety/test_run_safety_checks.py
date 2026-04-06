"""Edit $MKLMKL/exec/safety.py"""

import re
import pytest
from mklists.errors import SafetyError
from mklists.exec.safety import SafetyConfig, run_safety_checks


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

    with pytest.raises(SafetyError):
        run_safety_checks(tmp_path, safety_config)


def test_run_safety_checks_skips_dotfiles(tmp_path, safety_config):
    """Dotfiles (.rules, .mklistsrc) are skipped — they are config files, not data files."""
    (tmp_path / "data.txt").write_text("alpha\nbeta\n")
    (tmp_path / ".rules").write_text("# blank lines are fine\n\n0|.|data.txt|data.txt|\n")
    (tmp_path / ".mklistsrc").write_text("verbose: False\n\nbackup:\n  backup_enabled: False\n")

    run_safety_checks(tmp_path, safety_config)
