"""Validate that a given data directory satisfies mklists safety constraints."""

import stat
from pathlib import Path
from mklists.config import SafetyConfig


CATEGORY_FILENAME = "filename"
CATEGORY_METADATA = "metadata"
CATEGORY_CONTENT = "content"
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
        - Directory entries are all files.
        - Filenames are valid.
        - Files are regular files and not executable.
        - Files do not have binary content or blank lines.
    """
    for entry in datadir.iterdir():
        _check_is_regular_file(entry)
        _check_is_valid_name(entry.name, safety_cfg)
        _check_file_contents(entry)


def _check_is_regular_file(pathname: Path) -> None:
    """Verify that given pathname refers to a regular file based on its metadata.

    Args:
        pathname: Pathname to be checked.

    Raises:
        ValueError: If pathname is anything other than a regular file.
    """
    try:
        st = pathname.lstat()
    except OSError as e:
        raise ValueError(
            {
                "category": CATEGORY_METADATA,
                "reason": "cannot stat directory entry",
                "filename": pathname.name,
                "detail": str(e),
            }
        ) from e

    # reject symlinks explicitly
    if stat.S_ISLNK(st.st_mode):
        raise ValueError(
            {
                "category": CATEGORY_METADATA,
                "reason": "is symlink.",
                "filename": pathname.name,
            }
        )

    # reject anything that is not a regular file
    if not stat.S_ISREG(st.st_mode):
        raise ValueError(
            {
                "category": CATEGORY_METADATA,
                "reason": "is not a regular file.",
                "filename": pathname.name,
            }
        )

    # reject executable files
    if st.st_mode & stat.S_IXUSR:
        raise ValueError(
            {
                "category": CATEGORY_METADATA,
                "reason": "is executable.",
                "filename": pathname.name,
            }
        )


def _check_is_valid_name(filename: str, safety: SafetyConfig) -> None:
    """Verify that a filename satisfies safety constraints.

    Args:
        filename: Name of file (without path components).
        safety: Normalized safety configuration object.

    Returns:
        None, unless exceptions related to safety are raised.

    Raises:
        ValueError: If filename violates any safety rule.

    Note:
        Validates filenames against a configured set of forbidden filename patterns.
    """
    for pat in safety.invalid_filename_patterns:
        if pat.search(filename):
            raise ValueError(
                {
                    "category": CATEGORY_FILENAME,
                    "reason": "matches forbidden filename pattern",
                    "filename": filename,
                    "pattern": pat.pattern,
                }
            )


def _check_file_contents(filename: Path) -> None:
    """Verify that file content satisfies safety constraints.

    Args:
        filename: Path to file.

    Raises:
        ValueError: If content safety rules are violated.

    Note:
        File is read in two passes:
        - must not appear to be binary (no NUL bytes).
        - must contain no blank or whitespace-only lines.
    """
    with filename.open("rb") as f:
        chunk = f.read(_BINARY_SCAN_BYTES)
        if b"\x00" in chunk:
            raise ValueError(
                {
                    "category": CATEGORY_CONTENT,
                    "reason": "appears to be binary",
                    "filename": filename.name,
                }
            )

    with filename.open("rt", encoding="utf-8", errors="strict") as f:
        for lineno, line in enumerate(f, start=1):
            if line.strip() == "":
                raise ValueError(
                    {
                        "category": CATEGORY_CONTENT,
                        "reason": "has blank or whitespace-only line",
                        "filename": filename.name,
                        "lineno": lineno,
                    }
                )
