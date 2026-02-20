"""@@@"""

from pathlib import Path
import pytest
from mklists.config import _make_backup_config


def test_make_backup_config_given_relative_return_relative():
    """Given relative directory name, return absolute pathname."""
    config_rootdir = Path("/repo/root")

    config_dict = {
        "backup": {
            "backup_enabled": True,
            "backup_dir": "backups",
            "backup_depth": 3,
        }
    }

    backup_cfg = _make_backup_config(
        config_dict=config_dict,
        config_rootdir=config_rootdir,
    )

    assert backup_cfg.backup_enabled is True
    assert backup_cfg.backup_depth == 3
    assert backup_cfg.backup_dir == (config_rootdir / "backups").resolve()
    assert backup_cfg.backup_dir.is_absolute()


def test_make_backup_config_type_coercion():
    """Tests type coercion."""
    config_rootdir = Path("/repo/root")

    config_dict = {
        "backup": {
            "backup_enabled": 1,  # truthy
            "backup_dir": "bk",
            "backup_depth": "5",  # string → int
        }
    }

    backup_cfg = _make_backup_config(config_dict, config_rootdir)

    assert backup_cfg.backup_enabled is True
    assert backup_cfg.backup_depth == 5


def test_make_backup_config_rejects_nested_relative_backup_dir(tmp_path):
    """Relative backup_dir with multiple path components is invalid."""
    config_dict = {
        "backup": {
            "backup_enabled": True,
            "backup_dir": "runs/backups",
            "backup_depth": 3,
        }
    }

    with pytest.raises(
        ValueError,
        match="backup_dir must be single directory name or absolute pathname.",
    ):
        _make_backup_config(
            config_dict=config_dict,
            config_rootdir=tmp_path,
        )
