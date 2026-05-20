"""Initialize logger for a mklists run."""

import logging
import sys
from pathlib import Path

logger = logging.getLogger("mklists")


def init_logger(
    *,
    logfile: Path | None,
    verbose: bool,
) -> logging.Logger:
    """Initialize the mklists logger for a run.

    Args:
        logfile: Path of logfile, or None if no logfile is written.
        verbose: If True, print run progress to console.

    Returns:
        Configured Logger instance.
    """
    logger.setLevel(logging.DEBUG)
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    if verbose:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

    if logfile is not None:
        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        )
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

    return logger
