"""@@@"""

from pathlib import Path
import pytest
from mklists.config.resolve import _make_backup_config


def test_make_backup_config_given_relative_return_relative():
    """Given relative directory name, return absolute pathname."""
    config_rootdir = Path("/repo/root")

    config_dict = {
        "backup": {
            "backup_enabled": True,
            "backup_rootdir": "backups",
            "backup_depth": 3,
        }
    }

    backup_cfg = _make_backup_config(
        config_dict=config_dict,
        config_rootdir=config_rootdir,
    )

    assert backup_cfg.backup_enabled is True
    assert backup_cfg.backup_depth == 3
    assert backup_cfg.backup_rootdir == (config_rootdir / "backups").resolve()
    assert backup_cfg.backup_rootdir.is_absolute()


def test_make_backup_config_type_coercion():
    """Tests type coercion."""
    config_rootdir = Path("/repo/root")

    config_dict = {
        "backup": {
            "backup_enabled": 1,  # truthy
            "backup_rootdir": "bk",
            "backup_depth": "5",  # string → int
        }
    }

    backup_cfg = _make_backup_config(
        config_dict=config_dict, config_rootdir=config_rootdir
    )

    assert backup_cfg.backup_enabled is True
    assert backup_cfg.backup_depth == 5


def test_make_backup_config_null_backup_rootdir_raises(tmp_path):
    """backup_rootdir configured as null raises ValueError."""
    config_dict = {
        "backup": {
            "backup_enabled": True,
            "backup_rootdir": None,
            "backup_depth": 3,
        }
    }

    with pytest.raises(ValueError, match="backup_rootdir must not be configured as null"):
        _make_backup_config(config_dict=config_dict, config_rootdir=tmp_path)


def test_make_backup_config_absolute_backup_rootdir_used_as_is(tmp_path):
    """Absolute backup_rootdir is used directly without resolving against config_rootdir."""
    absolute_backup_rootdir = "/absolute/backup/path"

    config_dict = {
        "backup": {
            "backup_enabled": True,
            "backup_rootdir": absolute_backup_rootdir,
            "backup_depth": 3,
        }
    }

    backup_cfg = _make_backup_config(
        config_dict=config_dict,
        config_rootdir=tmp_path,
    )

    assert backup_cfg.backup_rootdir == Path(absolute_backup_rootdir)


def test_make_backup_config_rejects_nested_relative_backup_rootdir(tmp_path):
    """Relative backup_rootdir with multiple path components is invalid."""
    config_dict = {
        "backup": {
            "backup_enabled": True,
            "backup_rootdir": "runs/backups",
            "backup_depth": 3,
        }
    }

    with pytest.raises(
        ValueError,
        match=r".+ must be directory name or absolute path, not relative\.",
    ):
        _make_backup_config(
            config_dict=config_dict,
            config_rootdir=tmp_path,
        )
