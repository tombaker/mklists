"""Tests $MKLMKL/exec/safety.py"""

import os
import pytest
from mklists.exec.safety import _check_is_regular_file


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


def test_executable_file_fails(tmp_path):
    """If file is executable, raise ValueError."""
    p = tmp_path / "script.sh"
    p.write_text("echo hi\n")
    p.chmod(0o755)

    with pytest.raises(ValueError) as exc:
        _check_is_regular_file(pathname=p)

    err = exc.value.args[0]
    assert err["category"] == "metadata"
    assert err["reason"] == "is executable."


def test_directory_fails(tmp_path):
    """Directory tmp_path is not a regular file, raise ValueError."""
    with pytest.raises(ValueError) as exc:
        _check_is_regular_file(pathname=tmp_path)

    err = exc.value.args[0]
    assert err["reason"] == "is not a regular file."


@pytest.mark.skipif(os.name == "nt", reason="symlink semantics differ on Windows")
def test_check_directory_contents_rejects_symlink(tmp_path):
    """Symlink is not a regular file, raise ValueError."""
    target = tmp_path / "target.txt"
    target.write_text("x\n")

    symlink_to_target = tmp_path / "link.txt"
    symlink_to_target.symlink_to(target)

    with pytest.raises(ValueError):
        _check_is_regular_file(symlink_to_target)
