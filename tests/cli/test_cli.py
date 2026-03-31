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


def test_run_exits_cleanly_on_valid_datadir(tmp_path):
    """mklists run exits with code 0 when given a valid datadir.

    Minimal setup: a .rules file with one identity rule (all lines stay in
    input.txt), and an input.txt file with one line of content.
    """
    (tmp_path / ".rules").write_text("0|.|input.txt|input.txt|\n")
    (tmp_path / "input.txt").write_text("hello\n")

    result = CliRunner().invoke(cli, ["run", "-C", str(tmp_path)])
    assert result.exit_code == 0


def test_run_exits_cleanly_without_C_option(tmp_path, monkeypatch):
    """mklists run with no -C uses the current working directory."""
    (tmp_path / ".rules").write_text("0|.|input.txt|input.txt|\n")
    (tmp_path / "input.txt").write_text("hello\n")
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(cli, ["run"])
    assert result.exit_code == 0


def test_run_exits_with_error_on_invalid_dir(tmp_path):
    """mklists run exits with code 1 when given a directory with no mklists markers."""
    result = CliRunner().invoke(cli, ["run", "-C", str(tmp_path)])
    assert result.exit_code == 1
