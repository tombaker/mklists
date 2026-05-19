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


def test_init_datadir_rules_file_has_example_content_by_default(tmp_path):
    """mklists init datadir populates .rules with example content by default."""
    CliRunner().invoke(cli, ["init", "datadir", str(tmp_path)])
    assert (tmp_path / ".rules").read_text() == EXAMPLE_RULES


def test_init_datadir_bare_creates_empty_rules_file(tmp_path):
    """mklists init datadir --bare creates an empty .rules."""
    CliRunner().invoke(cli, ["init", "datadir", "--bare", str(tmp_path)])
    assert (tmp_path / ".rules").read_text() == ""


def test_init_datadir_bare_self_contained_creates_empty_mklistsrc(tmp_path):
    """mklists init datadir --bare --self-contained creates an empty .mklistsrc."""
    CliRunner().invoke(cli, ["init", "datadir", "--bare", "--self-contained", str(tmp_path)])
    assert (tmp_path / ".mklistsrc").read_text() == ""


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


def test_init_datatree_creates_mklists_yaml(tmp_path):
    """mklists init datatree always creates mklists.yaml."""
    CliRunner().invoke(cli, ["init", "datatree", str(tmp_path)])
    assert (tmp_path / "mklists.yaml").exists()


def test_init_datatree_creates_mklists_rules(tmp_path):
    """mklists init datatree always creates mklists.rules."""
    CliRunner().invoke(cli, ["init", "datatree", str(tmp_path)])
    assert (tmp_path / "mklists.rules").exists()


def test_init_datatree_mklists_rules_has_example_content(tmp_path):
    """mklists init datatree populates mklists.rules with example content."""
    CliRunner().invoke(cli, ["init", "datatree", str(tmp_path)])
    assert (tmp_path / "mklists.rules").read_text() == EXAMPLE_RULES


def test_init_datatree_creates_no_subdirs(tmp_path):
    """mklists init datatree does not create any datadir subdirectories."""
    CliRunner().invoke(cli, ["init", "datatree", str(tmp_path)])
    subdirs = [p for p in tmp_path.iterdir() if p.is_dir()]
    assert subdirs == []


def test_init_datatree_prints_advisory_message(tmp_path):
    """mklists init datatree prints advice to run mklists init datadir."""
    result = CliRunner().invoke(cli, ["init", "datatree", str(tmp_path)])
    assert "mklists init datadir" in result.output


def test_init_datatree_conflict_exits_with_error(tmp_path):
    """mklists init datatree exits with code 1 if mklists.yaml already exists."""
    (tmp_path / "mklists.yaml").write_text("")
    result = CliRunner().invoke(cli, ["init", "datatree", str(tmp_path)])
    assert result.exit_code == 1


# ── mklists init datadir — parent check ──────────────────────────────────────


def test_init_datadir_prints_parent_datatree_files(tmp_path):
    """mklists init datadir prints paths of datatree files found in parent."""
    (tmp_path / "mklists.yaml").write_text("")
    (tmp_path / "mklists.rules").write_text("")
    subdir = tmp_path / "sub"
    subdir.mkdir()
    result = CliRunner().invoke(cli, ["init", "datadir", str(subdir)])
    assert str(tmp_path / "mklists.yaml") in result.output
    assert str(tmp_path / "mklists.rules") in result.output


def test_init_datadir_no_parent_output_when_no_datatree_files(tmp_path):
    """mklists init datadir prints nothing about parent when no datatree files exist."""
    subdir = tmp_path / "sub"
    subdir.mkdir()
    result = CliRunner().invoke(cli, ["init", "datadir", str(subdir)])
    assert "Found in parent" not in result.output


def test_init_datadir_self_contained_skips_parent_check(tmp_path):
    """mklists init datadir --self-contained does not print parent datatree files."""
    (tmp_path / "mklists.yaml").write_text("")
    subdir = tmp_path / "sub"
    subdir.mkdir()
    result = CliRunner().invoke(cli, ["init", "datadir", "--self-contained", str(subdir)])
    assert "Found in parent" not in result.output



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
