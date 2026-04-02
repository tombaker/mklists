"""Tests for CLI entry point."""

from click.testing import CliRunner
from mklists.cli import cli
from mklists.init.datadir import EXAMPLE_RULES


# ── mklists init ──────────────────────────────────────────────────────────────


def test_init_exits_cleanly():
    """mklists init exits with code 0."""
    result = CliRunner().invoke(cli, ["init"])
    assert result.exit_code == 0


def test_init_outputs_message():
    """mklists init outputs a message containing 'init'."""
    result = CliRunner().invoke(cli, ["init"])
    assert "init" in result.output.lower()


# ── mklists init datadir ──────────────────────────────────────────────────────


def test_init_datadir_creates_rules_file(tmp_path):
    """mklists init datadir always creates .rules."""
    result = CliRunner().invoke(cli, ["init", "datadir", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / ".rules").exists()


def test_init_datadir_rules_file_empty_by_default(tmp_path):
    """mklists init datadir creates an empty .rules without --rules."""
    CliRunner().invoke(cli, ["init", "datadir", str(tmp_path)])
    assert (tmp_path / ".rules").read_text() == ""


def test_init_datadir_rules_flag_populates_rules_file(tmp_path):
    """mklists init datadir --rules populates .rules with example content."""
    CliRunner().invoke(cli, ["init", "datadir", "--rules", str(tmp_path)])
    assert (tmp_path / ".rules").read_text() == EXAMPLE_RULES


def test_init_datadir_no_mklistsrc_by_default(tmp_path):
    """mklists init datadir does not create .mklistsrc without --self-contained."""
    CliRunner().invoke(cli, ["init", "datadir", str(tmp_path)])
    assert not (tmp_path / ".mklistsrc").exists()


def test_init_datadir_self_contained_creates_mklistsrc(tmp_path):
    """mklists init datadir --self-contained creates .mklistsrc."""
    result = CliRunner().invoke(cli, ["init", "datadir", "--self-contained", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / ".mklistsrc").exists()


def test_init_datadir_conflict_exits_with_error(tmp_path):
    """mklists init datadir exits with code 1 if .rules already exists."""
    (tmp_path / ".rules").write_text("")
    result = CliRunner().invoke(cli, ["init", "datadir", str(tmp_path)])
    assert result.exit_code == 1


# ── mklists init datatree ─────────────────────────────────────────────────────


def test_init_datatree_creates_subdirs(tmp_path):
    """mklists init datatree always creates default subdirs a/ and b/."""
    result = CliRunner().invoke(cli, ["init", "datatree", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "a").is_dir()
    assert (tmp_path / "b").is_dir()


def test_init_datatree_creates_mklists_yaml(tmp_path):
    """mklists init datatree always creates mklists.yaml."""
    CliRunner().invoke(cli, ["init", "datatree", str(tmp_path)])
    assert (tmp_path / "mklists.yaml").exists()


def test_init_datatree_creates_mklists_rules(tmp_path):
    """mklists init datatree always creates mklists.rules."""
    CliRunner().invoke(cli, ["init", "datatree", str(tmp_path)])
    assert (tmp_path / "mklists.rules").exists()


def test_init_datatree_creates_subdir_rules_files(tmp_path):
    """mklists init datatree always creates .rules in each subdir."""
    CliRunner().invoke(cli, ["init", "datatree", str(tmp_path)])
    assert (tmp_path / "a" / ".rules").exists()
    assert (tmp_path / "b" / ".rules").exists()


def test_init_datatree_rules_flag_populates_all_rules_files(tmp_path):
    """mklists init datatree --rules populates all rule files with example content."""
    CliRunner().invoke(cli, ["init", "datatree", "--rules", str(tmp_path)])
    assert (tmp_path / "mklists.rules").read_text() == EXAMPLE_RULES
    assert (tmp_path / "a" / ".rules").read_text() == EXAMPLE_RULES
    assert (tmp_path / "b" / ".rules").read_text() == EXAMPLE_RULES


def test_init_datatree_custom_subdirs(tmp_path):
    """mklists init datatree --subdirs creates the named subdirs."""
    result = CliRunner().invoke(cli, ["init", "datatree", "--subdirs", "x,y", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "x").is_dir()
    assert (tmp_path / "y").is_dir()
    assert not (tmp_path / "a").exists()


def test_init_datatree_conflict_exits_with_error(tmp_path):
    """mklists init datatree exits with code 1 if a named subdir already exists."""
    (tmp_path / "a").mkdir()
    result = CliRunner().invoke(cli, ["init", "datatree", str(tmp_path)])
    assert result.exit_code == 1



def test_run_exits_cleanly_on_valid_datadir(tmp_path):
    """mklists run exits with code 0 when given a valid datadir.

    Minimal setup: a .rules file with one identity rule (all lines stay in
    input.txt), and an input.txt file with one line of content.
    """
    (tmp_path / ".rules").write_text("0|.|input.txt|output.txt|\n")
    (tmp_path / "input.txt").write_text("hello\n")

    result = CliRunner().invoke(cli, ["run", "-C", str(tmp_path)])
    assert result.exit_code == 0


def test_run_exits_cleanly_without_C_option(tmp_path, monkeypatch):
    """mklists run with no -C uses the current working directory."""
    (tmp_path / ".rules").write_text("0|.|input.txt|output.txt|\n")
    (tmp_path / "input.txt").write_text("hello\n")
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(cli, ["run"])
    assert result.exit_code == 0


def test_run_exits_with_error_on_invalid_dir(tmp_path):
    """mklists run exits with code 1 when given a directory with no mklists markers."""
    result = CliRunner().invoke(cli, ["run", "-C", str(tmp_path)])
    assert result.exit_code == 1
