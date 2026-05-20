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
    """Verbose logging should route INFO messages to stdout."""
    init_logger(logfile=None, verbose=True)
    logging.getLogger("mklists").info("test message")

    captured = capsys.readouterr()
    assert "test message" in captured.out
    assert captured.err == ""


def test_logfile_logging_creates_file(tmp_path):
    """Logfile logging should create a logfile and write logged messages to it."""
    init_logger(logfile=tmp_path / "run.log", verbose=False)
    logging.getLogger("mklists").info("test message")

    logfile = tmp_path / "run.log"
    assert logfile.exists()
    assert "test message" in logfile.read_text()


# ── caplog-based: log record content ─────────────────────────────────────────


def test_verbose_emits_log_records(caplog):
    """init_logger with verbose=True routes INFO records to caplog."""
    with caplog.at_level(logging.INFO, logger="mklists"):
        init_logger(logfile=None, verbose=True)
        logging.getLogger("mklists").info("test message")

    assert any("test message" in r.message for r in caplog.records)


def test_not_verbose_no_log_records(caplog):
    """init_logger with verbose=False and no logfile emits no log records."""
    with caplog.at_level(logging.INFO, logger="mklists"):
        init_logger(logfile=None, verbose=False)

    assert caplog.records == []


def test_verbose_record_level_is_info(caplog):
    """Messages logged at INFO level appear with levelno INFO."""
    with caplog.at_level(logging.INFO, logger="mklists"):
        init_logger(logfile=None, verbose=True)
        logging.getLogger("mklists").info("test message")

    records = [r for r in caplog.records if "test message" in r.message]
    assert len(records) == 1
    assert records[0].levelno == logging.INFO
