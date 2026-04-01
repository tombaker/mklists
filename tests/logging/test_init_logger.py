"""Tests for src/mklists/logging.py"""

import logging

import pytest

from mklists.logging import init_logger


@pytest.fixture(autouse=True)
def clean_mklists_logger():
    """Remove all handlers from the mklists logger after each test."""
    yield
    lg = logging.getLogger("mklists")
    for handler in lg.handlers[:]:
        handler.close()
        lg.removeHandler(handler)


# ── capsys-based: observable stdout/stderr behaviour ─────────────────────────


def test_no_outputs_no_logging(capsys):
    """If verbose not True and no logfile is passed, nothing is emitted."""
    init_logger(
        logfile=None,
        verbose=False,
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_verbose_logging_writes_to_stdout(capsys):
    """Verbose logging should emit to stdout."""
    init_logger(
        logfile=None,
        verbose=True,
    )

    captured = capsys.readouterr()
    assert "Start mklists run." in captured.out
    assert captured.err == ""


def test_logfile_logging_creates_file(tmp_path):
    """Logfile logging should create a logfile and write the run header."""
    init_logger(
        logfile=tmp_path / "run.log",
        verbose=False,
    )

    logfile = tmp_path / "run.log"
    assert logfile.exists()

    contents = logfile.read_text()
    assert "Start mklists run." in contents


# ── caplog-based: log record content ─────────────────────────────────────────


def test_verbose_emits_start_message_as_log_record(caplog):
    """init_logger with verbose=True emits the start message as an INFO record."""
    with caplog.at_level(logging.INFO, logger="mklists"):
        init_logger(logfile=None, verbose=True)

    assert any("Start mklists run." in r.message for r in caplog.records)


def test_not_verbose_no_log_records(caplog):
    """init_logger with verbose=False and no logfile emits no log records."""
    with caplog.at_level(logging.INFO, logger="mklists"):
        init_logger(logfile=None, verbose=False)

    assert caplog.records == []


def test_verbose_record_level_is_info(caplog):
    """The start message is emitted at INFO level."""
    with caplog.at_level(logging.INFO, logger="mklists"):
        init_logger(logfile=None, verbose=True)

    start_records = [r for r in caplog.records if "Start mklists run." in r.message]
    assert len(start_records) == 1
    assert start_records[0].levelno == logging.INFO
