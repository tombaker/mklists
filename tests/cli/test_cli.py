"""Tests for CLI entry point."""

from click.testing import CliRunner
from mklists.cli import cli


def test_init_exits_cleanly():
    """mklists init exits with code 0."""
    result = CliRunner().invoke(cli, ["init"])
    assert result.exit_code == 0


def test_init_outputs_message():
    """mklists init outputs a message containing 'init'."""
    result = CliRunner().invoke(cli, ["init"])
    assert "init" in result.output.lower()


def test_run_exits_cleanly():
    """mklists run exits with code 0."""
    result = CliRunner().invoke(cli, ["run"])
    assert result.exit_code == 0


def test_run_outputs_message():
    """mklists run outputs a message containing 'run'."""
    result = CliRunner().invoke(cli, ["run"])
    assert "run" in result.output.lower()
