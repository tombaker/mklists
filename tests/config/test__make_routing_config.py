"""Tests for $MKLMKL/config.py"""

from pathlib import Path
import pytest
from mklists.config.resolve import _make_routing_config


def _config_dict(routing_dict):
    return {
        "routing": {
            "routing_enabled": True,
            "routing_dict": routing_dict,
        }
    }


def test_make_routing_config_filename_with_path_separator_raises(tmp_path):
    """Routing key with a path separator raises ValueError."""
    with pytest.raises(ValueError, match="must be a single filename, not a path"):
        _make_routing_config(
            config_dict=_config_dict({"subdir/file.txt": "dest"}),
            config_rootdir=tmp_path,
        )


def test_make_routing_config_relative_dirname_with_multiple_parts_raises(tmp_path):
    """Routing value that is a relative path with multiple components raises ValueError."""
    with pytest.raises(ValueError, match="must be a directory name or absolute path"):
        _make_routing_config(
            config_dict=_config_dict({"file.txt": "subdir/dest"}),
            config_rootdir=tmp_path,
        )


def test_make_routing_config_plain_filename_is_valid(tmp_path):
    """Routing key that is a plain filename (one part) is accepted."""
    cfg = _make_routing_config(
        config_dict=_config_dict({"file.txt": "dest"}),
        config_rootdir=tmp_path,
    )

    assert "file.txt" in cfg.routing_dict


def test_make_routing_config_dirname_resolved_against_config_rootdir(tmp_path):
    """Single-part dirname is resolved as config_rootdir / dirname."""
    cfg = _make_routing_config(
        config_dict=_config_dict({"file.txt": "dest"}),
        config_rootdir=tmp_path,
    )

    assert cfg.routing_dict["file.txt"] == (tmp_path / "dest").resolve()
