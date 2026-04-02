"""Tests for _make_linkify_config in $MKLMKL/config/resolve.py"""

from pathlib import Path
import pytest
from mklists.config.resolve import _make_linkify_config


def _config_dict(linkify_md_dir=None, linkify_html_dir=None):
    return {
        "linkify": {
            "linkify_md_dir": linkify_md_dir,
            "linkify_html_dir": linkify_html_dir,
        }
    }


def test_make_linkify_config_both_null_returns_disabled(tmp_path):
    """Both dirs null returns a fully disabled LinkifyConfig."""
    cfg = _make_linkify_config(config_dict=_config_dict(), config_rootdir=tmp_path)

    assert cfg.linkify_md_dir is None
    assert cfg.linkify_html_dir is None


def test_make_linkify_config_md_dir_relative_resolved_against_config_rootdir(tmp_path):
    """Relative linkify_md_dir is resolved against config_rootdir."""
    cfg = _make_linkify_config(config_dict=_config_dict(linkify_md_dir=".linkify"), config_rootdir=tmp_path)

    assert cfg.linkify_md_dir == (tmp_path / ".linkify").resolve()


def test_make_linkify_config_html_dir_relative_resolved_against_config_rootdir(tmp_path):
    """Relative linkify_html_dir is resolved against config_rootdir."""
    cfg = _make_linkify_config(config_dict=_config_dict(linkify_html_dir=".linkify_html"), config_rootdir=tmp_path)

    assert cfg.linkify_html_dir == (tmp_path / ".linkify_html").resolve()


def test_make_linkify_config_md_dir_absolute_used_as_is(tmp_path):
    """Absolute linkify_md_dir is used directly, config_rootdir has no effect."""
    cfg = _make_linkify_config(
        config_dict=_config_dict(linkify_md_dir="/absolute/linkify"),
        config_rootdir=tmp_path,
    )

    assert cfg.linkify_md_dir == Path("/absolute/linkify").resolve()


def test_make_linkify_config_both_dirs_set(tmp_path):
    """Both dirs can be set independently."""
    cfg = _make_linkify_config(
        config_dict=_config_dict(linkify_md_dir=".linkify", linkify_html_dir=".linkify_html"),
        config_rootdir=tmp_path,
    )

    assert cfg.linkify_md_dir == (tmp_path / ".linkify").resolve()
    assert cfg.linkify_html_dir == (tmp_path / ".linkify_html").resolve()
