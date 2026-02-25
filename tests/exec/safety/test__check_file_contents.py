"""Edit $MKLMKL/exec/safety.py"""

import pytest
from mklists.exec.safety import _check_file_contents


def test_valid_text_file_passes(tmp_path):
    """Valid text file passes."""
    p = tmp_path / "data.txt"
    p.write_text("alpha\nbeta\ngamma\n")

    _check_file_contents(p)


def test_binary_file_fails(tmp_path):
    """If file looks binary, raise ValueError."""
    p = tmp_path / "data.bin"
    p.write_bytes(b"\x00\x01\x02hello")

    with pytest.raises(ValueError) as exc:
        _check_file_contents(p)

    err = exc.value.args[0]
    assert err["category"] == "content"
    assert err["reason"] == "appears to be binary"


def test_blank_line_fails(tmp_path):
    """If file has a blank line, raise ValueError."""
    p = tmp_path / "data.txt"
    p.write_text("alpha\n\nbeta\n")

    with pytest.raises(ValueError) as exc:
        _check_file_contents(p)

    err = exc.value.args[0]
    assert err["reason"] == "has blank or whitespace-only line"
    assert err["lineno"] == 2


def test_whitespace_only_line_fails(tmp_path):
    """If file has a whitespace-only line, raise ValueError."""
    p = tmp_path / "data.txt"
    p.write_text("alpha\n   \nbeta\n")

    with pytest.raises(ValueError) as exc:
        _check_file_contents(p)

    err = exc.value.args[0]
    assert err["lineno"] == 2


def test_invalid_utf8_fails(tmp_path):
    """If file is not valid UTF-8, raise ValueError."""
    p = tmp_path / "data.txt"
    p.write_bytes(b"alpha\n\xff\xfe\nbeta\n")

    with pytest.raises(ValueError):
        _check_file_contents(p)
