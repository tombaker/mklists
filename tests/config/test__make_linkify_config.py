"""Tests for _make_linkify_config in $MKLMKL/config/resolve.py"""

from pathlib import Path
import pytest
from mklists.config.resolve import _make_linkify_config


def _config_dict(linkify_dir):
    return {
        "linkify": {
            "linkify_enabled": True,
            "linkify_dir": linkify_dir,
        }
    }


def test_make_linkify_config_null_linkify_dir_raises(tmp_path):
    """linkify_dir configured as null raises ValueError."""
    with pytest.raises(ValueError, match="linkify_dir must not be configured as null"):
        _make_linkify_config(config_dict=_config_dict(None), config_rootdir=tmp_path)


def test_make_linkify_config_relative_dir_resolved_against_config_rootdir(tmp_path):
    """Relative linkify_dir is resolved against config_rootdir."""
    cfg = _make_linkify_config(config_dict=_config_dict("markdown"), config_rootdir=tmp_path)

    assert cfg.linkify_dir == (tmp_path / "markdown").resolve()


def test_make_linkify_config_absolute_dir_used_as_is(tmp_path):
    """Absolute linkify_dir is used directly, config_rootdir has no effect."""
    cfg = _make_linkify_config(
        config_dict=_config_dict("/absolute/markdown"),
        config_rootdir=tmp_path,
    )

    assert cfg.linkify_dir == Path("/absolute/markdown").resolve()
