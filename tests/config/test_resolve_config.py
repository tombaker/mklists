"""Tests for resolve_config."""

import re
from pathlib import Path
import pytest
from mklists.config.model import (
    BackupConfig,
    Config,
    LinkifyConfig,
    RoutingConfig,
    SafetyConfig,
)
from mklists.config.resolve import resolve_config
from mklists.errors import StructureError
from mklists.structure.markers import (
    DATADIR_CONFIGFILE_NAME,
    DATADIR_RULEFILE_NAME,
    REPO_CONFIGFILE_NAME,
)
from mklists.structure.model import (
    DatadirStructuralContext,
    StartdirStructuralContext,
    StructuralContext,
)


def make_structural_context(
    startdir: Path,
    *,
    repo_configfile_found: Path | None = None,
    repo_rulefile_found: Path | None = None,
    datadir_configfile_found: Path | None = None,
    datadir_rulefile_found: Path | None = None,
    datadir_contexts: list[DatadirStructuralContext] | None = None,
) -> StructuralContext:
    """Build a StructuralContext for testing."""
    return StructuralContext(
        startdir_context=StartdirStructuralContext(
            startdir=startdir,
            repo_configfile_found=repo_configfile_found,
            repo_rulefile_found=repo_rulefile_found,
            datadir_configfile_found=datadir_configfile_found,
            datadir_rulefile_found=datadir_rulefile_found,
        ),
        datadir_contexts=datadir_contexts or [],
    )


# --- is_repo_root ---


def test_resolve_config_repo_root_with_configfile_returns_config(tmp_path):
    """Repo root with config file uses that file and returns a Config."""
    configfile = tmp_path / REPO_CONFIGFILE_NAME
    configfile.write_text("verbose: true\n")

    fake_ctx = make_structural_context(
        startdir=tmp_path,
        repo_configfile_found=configfile,
    )
    config = resolve_config(fake_ctx)

    assert isinstance(config, Config)
    assert config.configfile_used == configfile
    assert config.config_rootdir == tmp_path
    assert config.verbose is True


def test_resolve_config_repo_root_rulefile_only_uses_defaults(tmp_path):
    """Repo root with only a rule file has configfile_used=None and uses defaults."""
    rulefile = tmp_path / "mklists.rules"
    rulefile.touch()

    fake_ctx = make_structural_context(startdir=tmp_path, repo_rulefile_found=rulefile)
    config = resolve_config(fake_ctx)

    assert config.configfile_used is None


# --- is_datadir_selfcontained ---


def test_resolve_config_selfcontained_datadir_uses_local_configfile(tmp_path):
    """Self-contained datadir uses its own config file."""
    local_configfile = tmp_path / DATADIR_CONFIGFILE_NAME
    local_configfile.write_text("verbose: true\n")
    rulefile = tmp_path / DATADIR_RULEFILE_NAME
    rulefile.touch()

    fake_ctx = make_structural_context(
        startdir=tmp_path,
        datadir_configfile_found=local_configfile,
        datadir_rulefile_found=rulefile,
    )
    config = resolve_config(fake_ctx)

    assert config.configfile_used == local_configfile
    assert config.config_rootdir == tmp_path
    assert config.verbose is True


# --- is_datadir_in_repo ---


def test_resolve_config_datadir_in_repo_finds_parent_configfile(tmp_path):
    """Datadir in repo uses repo config file found in its parent directory."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    repo_configfile = tmp_path / REPO_CONFIGFILE_NAME
    repo_configfile.write_text("verbose: true\n")
    rulefile = datadir / "mklists.rules"
    rulefile.touch()

    fake_ctx = make_structural_context(
        startdir=datadir, datadir_rulefile_found=rulefile
    )
    config = resolve_config(fake_ctx)

    assert config.configfile_used == repo_configfile
    assert config.config_rootdir == tmp_path  # startdir.parent
    assert config.verbose is True


def test_resolve_config_datadir_in_repo_no_parent_configfile_uses_defaults(tmp_path):
    """Datadir in repo with no parent config file uses defaults."""
    datadir = tmp_path / "data"
    datadir.mkdir()
    rulefile = datadir / "mklists.rules"
    rulefile.touch()

    fake_ctx = make_structural_context(
        startdir=datadir, datadir_rulefile_found=rulefile
    )
    config = resolve_config(fake_ctx)

    assert config.configfile_used is None
    assert config.verbose is False  # This will break if default settings change.


# --- unreachable structural state ---


def test_resolve_config_unreachable_state_raises_structure_error(tmp_path):
    """No recognized structural state raises StructureError."""
    fake_ctx = make_structural_context(startdir=tmp_path)

    with pytest.raises(StructureError, match="Unreachable structural state."):
        resolve_config(fake_ctx)


def test_resolve_config_else_branch_raises_structure_error(tmp_path, mocker):
    """The else branch in resolve_config (line 46) raises StructureError.

    This branch is doubly unreachable in normal execution: the config_rootdir
    property on StartdirStructuralContext performs the same three-way check and
    raises StructureError before resolve_config can reach its own else clause.
    The existing test above triggers the property raise (line 32), not line 46.

    To cover line 46 directly, this test mocks startdir_context so that
    config_rootdir returns a valid Path (preventing the early raise) while all
    three structural predicates remain False. This documents the contract that
    resolve_config itself guards against invalid structural state independently
    of the property, so that if the property guard is ever removed or the
    if/elif logic is refactored, a StructureError is still raised here.
    """
    mock_startdir_ctx = mocker.MagicMock()
    mock_startdir_ctx.config_rootdir = tmp_path
    mock_startdir_ctx.is_repo_root = False
    mock_startdir_ctx.is_datadir_selfcontained = False
    mock_startdir_ctx.is_datadir_in_repo = False

    mock_ctx = mocker.MagicMock()
    mock_ctx.startdir_context = mock_startdir_ctx

    with pytest.raises(StructureError, match="Unreachable structural state."):
        resolve_config(mock_ctx)


# --- returned Config contents ---


def test_resolve_config_returns_config_with_expected_sub_configs(tmp_path):
    """Returned Config has the expected sub-config types."""
    fake_ctx = make_structural_context(
        startdir=tmp_path, repo_rulefile_found=tmp_path / "mklists.rules"
    )
    config = resolve_config(fake_ctx)

    assert isinstance(config.backup, BackupConfig)
    assert isinstance(config.linkify, LinkifyConfig)
    assert isinstance(config.routing, RoutingConfig)
    assert isinstance(config.safety, SafetyConfig)


def test_resolve_config_default_backup_values(tmp_path):
    """Default config has backup disabled, depth 3, rootdir under config_rootdir.
    
    This test, and tests below, will fail if DEFAULT_CONFIG_YAML is changed.
    """
    fake_ctx = make_structural_context(
        startdir=tmp_path, repo_rulefile_found=tmp_path / "mklists.rules"
    )
    config = resolve_config(fake_ctx)

    assert config.backup.backup_enabled is False
    assert config.backup.backup_depth == 3
    assert config.backup.backup_rootdir == (tmp_path / "backups").resolve()


def test_resolve_config_default_linkify_values(tmp_path):
    """Default config has linkify disabled and linkify_dir under config_rootdir."""
    fake_ctx = make_structural_context(
        startdir=tmp_path, repo_rulefile_found=tmp_path / "mklists.rules"
    )
    config = resolve_config(fake_ctx)

    assert config.linkify.linkify_enabled is False
    assert config.linkify.linkify_dir == (tmp_path / "markdown").resolve()


def test_resolve_config_default_safety_patterns_are_compiled_regexes(tmp_path):
    """Default safety patterns are compiled into re.Pattern instances."""
    fake_ctx = make_structural_context(
        startdir=tmp_path, repo_rulefile_found=tmp_path / "mklists.rules"
    )
    config = resolve_config(fake_ctx)

    assert isinstance(config.safety.invalid_filename_patterns, list)
    assert len(config.safety.invalid_filename_patterns) > 0
    assert all(
        isinstance(p, re.Pattern) for p in config.safety.invalid_filename_patterns
    )


def test_resolve_config_user_yaml_overrides_defaults(tmp_path):
    """User config values override defaults while unset values stay at defaults."""
    configfile = tmp_path / REPO_CONFIGFILE_NAME
    configfile.write_text("backup:\n  backup_enabled: true\n  backup_depth: 5\n")

    fake_ctx = make_structural_context(
        startdir=tmp_path, repo_configfile_found=configfile
    )
    config = resolve_config(fake_ctx)

    assert config.backup.backup_enabled is True
    assert config.backup.backup_depth == 5
    assert config.backup.backup_rootdir == (tmp_path / "backups").resolve()  # default


def test_resolve_config_invalid_regex_in_user_configfile_raises_value_error(tmp_path):
    """Invalid regex in user config file raises ValueError."""
    configfile = tmp_path / REPO_CONFIGFILE_NAME
    configfile.write_text("safety:\n  invalid_filename_patterns:\n    - '['\n")

    fake_ctx = make_structural_context(
        startdir=tmp_path, repo_configfile_found=configfile
    )

    with pytest.raises(ValueError, match="Invalid regex in config"):
        resolve_config(fake_ctx)
