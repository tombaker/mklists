"""Validate that a given data directory satisfies mklists safety constraints."""

import stat
from pathlib import Path

from mklists.config.model import SafetyConfig
from mklists.errors import SafetyError

_BINARY_SCAN_BYTES = 8192


def run_safety_checks(datadir: Path, safety_cfg: SafetyConfig) -> None:
    """Run safety checks.

    Args:
        datadir: Path of data directory.
        safety_cfg: Normalized safety configuration object.

    Returns:
        None, unless safety exceptions are raised.

    Note:
        Checks (from cheapest to most expensive):
        - Directory entries are all regular files.
        - Filenames are valid.
        - Files do not have binary content or blank lines.
    """
    for entry in datadir.iterdir():
        if entry.name.startswith("."):
            continue
        _check_is_regular_file(entry)
        _check_is_valid_name(entry, safety_cfg)
        _check_file_contents(entry)


def _check_is_regular_file(pathname: Path) -> None:
    """Verify that given pathname refers to a regular file based on its metadata.

    Args:
        pathname: Pathname to be checked.

    Raises:
        SafetyError: If pathname is anything other than a regular file.
    """
    try:
        st = pathname.lstat()
    except OSError as e:
        raise SafetyError(f"{pathname}: cannot stat: {e}") from e

    if stat.S_ISLNK(st.st_mode):
        raise SafetyError(f"{pathname}: is a symlink")

    if not stat.S_ISREG(st.st_mode):
        raise SafetyError(f"{pathname}: is not a regular file")


def _check_is_valid_name(pathname: Path, safety: SafetyConfig) -> None:
    """Verify that a filename satisfies safety constraints.

    Args:
        pathname: Full path to the file being checked.
        safety: Normalized safety configuration object.

    Returns:
        None, unless exceptions related to safety are raised.

    Raises:
        SafetyError: If filename violates any safety rule.

    Note:
        Validates filenames against a configured set of forbidden filename patterns.
    """
    for pat in safety.invalid_filename_patterns:
        if pat.search(pathname.name):
            raise SafetyError(
                f"'{pathname}' matches forbidden filename pattern {pat.pattern!r}.\n"
                f"Processing interrupted."
            )


def _check_file_contents(pathname: Path) -> None:
    """Verify that file content satisfies safety constraints.

    Args:
        pathname: Path to file.

    Raises:
        SafetyError: If content safety rules are violated.

    Note:
        File is read in two passes:
        - must not appear to be binary (no NUL bytes).
        - must contain no blank or whitespace-only lines.
    """
    with pathname.open("rb") as f:
        chunk = f.read(_BINARY_SCAN_BYTES)
        if b"\x00" in chunk:
            raise SafetyError(f"{pathname}: appears to be binary")

    try:
        with pathname.open("rt", encoding="utf-8", errors="strict") as f:
            for lineno, line in enumerate(f, start=1):
                if line.strip() == "":
                    raise SafetyError(
                        f"{pathname}: has blank or whitespace-only line at line {lineno}"
                    )
    except UnicodeDecodeError as e:
        raise SafetyError(f"{pathname}: is not valid UTF-8: {e}") from e
