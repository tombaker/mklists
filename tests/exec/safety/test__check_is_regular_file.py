"""Tests $MKLMKL/exec/safety.py"""

import os
import pytest
from mklists.errors import SafetyError
from mklists.exec.safety import _check_is_regular_file


def test_nonexistent_path_raises_safety_error(tmp_path):
    """Non-existent path causes lstat() to raise OSError, which is re-raised as SafetyError."""
    missing = tmp_path / "nonexistent.txt"

    with pytest.raises(SafetyError) as exc:
        _check_is_regular_file(pathname=missing)

    assert "cannot stat" in str(exc.value)


def test_regular_readable_file_passes(tmp_path):
    """File is a regular file."""
    a_file = tmp_path / "a.txt"
    a_file.write_text("a\n")

    _check_is_regular_file(pathname=a_file)


def test_check_file_is_regular_file_even_if_hidden(tmp_path):
    """File is a regular file even if hidden (just FYI...)."""
    a_rulefile = tmp_path / ".rules"
    a_rulefile.write_text("x\n")

    _check_is_regular_file(a_rulefile)


def test_directory_fails(tmp_path):
    """Directory tmp_path is not a regular file, raise SafetyError."""
    with pytest.raises(SafetyError) as exc:
        _check_is_regular_file(pathname=tmp_path)

    assert "is not a regular file" in str(exc.value)


@pytest.mark.skipif(os.name == "nt", reason="symlink semantics differ on Windows")
def test_check_directory_contents_rejects_symlink(tmp_path):
    """Symlink is not a regular file, raise SafetyError."""
    target = tmp_path / "target.txt"
    target.write_text("x\n")

    symlink_to_target = tmp_path / "link.txt"
    symlink_to_target.symlink_to(target)

    with pytest.raises(SafetyError) as exc:
        _check_is_regular_file(symlink_to_target)

    assert "is a symlink" in str(exc.value)
