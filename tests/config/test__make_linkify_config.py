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
    cfg = _make_linkify_config(
        config_dict=_config_dict(linkify_md_dir=".linkify"), config_rootdir=tmp_path
    )

    assert cfg.linkify_md_dir == (tmp_path / ".linkify").resolve()


def test_make_linkify_config_html_dir_relative_resolved_against_config_rootdir(
    tmp_path,
):
    """Relative linkify_html_dir is resolved against config_rootdir."""
    cfg = _make_linkify_config(
        config_dict=_config_dict(linkify_html_dir=".linkify_html"),
        config_rootdir=tmp_path,
    )

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
        config_dict=_config_dict(
            linkify_md_dir=".linkify", linkify_html_dir=".linkify_html"
        ),
        config_rootdir=tmp_path,
    )

    assert cfg.linkify_md_dir == (tmp_path / ".linkify").resolve()
    assert cfg.linkify_html_dir == (tmp_path / ".linkify_html").resolve()


def test_make_linkify_config_relative_dirname_with_multiple_parts_raises(tmp_path):
    """Relative value with more than one path component is invalid."""
    with pytest.raises(ValueError, match="must be a directory name or absolute path"):
        _make_linkify_config(
            config_dict=_config_dict(linkify_md_dir="subdir/md"),
            config_rootdir=tmp_path,
        )


def test_make_linkify_config_dotdot_alone_raises(tmp_path):
    """A bare '..' has a single path component but must still be rejected."""
    with pytest.raises(ValueError, match="must be a directory name or absolute path"):
        _make_linkify_config(
            config_dict=_config_dict(linkify_md_dir=".."),
            config_rootdir=tmp_path,
        )


def test_make_linkify_config_dotdot_prefixed_value_raises(tmp_path):
    """A relative value climbing out via '..' is invalid, even combined with a name."""
    with pytest.raises(ValueError, match="must be a directory name or absolute path"):
        _make_linkify_config(
            config_dict=_config_dict(linkify_html_dir="../_html"),
            config_rootdir=tmp_path,
        )
