"""Tests $MKLMKL/logging.py"""

import sys
from mklists.logging import _make_logsink_specs


def test_make_logsink_specs_verbose_only():
    """If verbose is True, logger sink is specified for output to sys.stdout."""
    specs = _make_logsink_specs(
        logfile=None,
        verbose=True,
    )

    assert len(specs) == 1
    assert specs[0].sink is sys.stdout


def test_logfile_relative_path(tmp_path):
    """If logfile path is specified, logger sink is specified for output to file."""
    specs = _make_logsink_specs(
        logfile=tmp_path / "logs" / "mklists.log",
        verbose=False,
    )

    assert len(specs) == 1
    spec = specs[0]
    assert spec.sink == tmp_path / "logs" / "mklists.log"
    assert spec.catch is True
