"""Tests for ~/github/tombaker/mklists/src/mklists/config_logger.py"""

from mklists.config_logger import init_logger


def test_no_outputs_no_logging(capsys):
    """If verbose not True and no logfile is passed, nothing is emitted."""
    init_logger(
        logfile_path=None,
        verbose=False,
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_verbose_logging_writes_to_stdout(capsys):
    """Verbose logging should emit to stdout."""
    init_logger(
        logfile_path=None,
        verbose=True,
    )

    captured = capsys.readouterr()
    assert "Start mklists run." in captured.out
    assert captured.err == ""


def test_logfile_logging_creates_file(tmp_path):
    """Logfile logging should create a logfile and write the run header.

    Note: `logfile_path` of `tmp_path / "run.log"` is good enough for a test.
    When used in context, `init_logger` would always be passed the absolute
    path of the backup directory for a given run.
    """
    init_logger(
        logfile_path=tmp_path / "run.log",
        verbose=False,
    )

    logfile = tmp_path / "run.log"
    assert logfile.exists()

    contents = logfile.read_text()
    assert "Start mklists run." in contents
