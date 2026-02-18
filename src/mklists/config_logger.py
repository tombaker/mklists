"""Initialize logger sinks and formats for a mklists run."""

from dataclasses import dataclass
import sys
from pathlib import Path
from typing import Any
from loguru import logger


@dataclass(frozen=True)
class _LogSinkSpec:
    sink: Any
    format: str
    level: str
    catch: bool = False


def init_logger(
    *,
    logfile: Path | None,
    verbose: bool,
) -> Any:
    """Initialize logger for a mklists run.

    Args:
        logfile: Path of logfile, or None if no logfile is written.
        verbose: If True, print run progress to console.

    Returns:
        Global singleton Logger instance, with sinks configured.

    Note:
        Removes any existing logger sinks before adding new ones.
    """
    logger.remove()

    sink_specs = _make_logsink_specs(logfile, verbose)

    for spec in sink_specs:
        logger.add(
            sink=spec.sink,
            format=spec.format,
            level=spec.level,
            catch=spec.catch,
        )

    if sink_specs:
        logger.info("Start mklists run.")

    return logger


def _make_logsink_specs(
    logfile: Path | None,
    verbose: bool,
) -> list[_LogSinkSpec]:
    """Return list of logsink-specification objects.

    Args:
        logfile: Absolute path of logfile, or None if no logfile is written.
        verbose: If True, print run progress to console.

    Returns:
        List of log-sink specification objects.
    """
    sink_specs: list[_LogSinkSpec] = []

    if verbose:
        sink_specs.append(
            _LogSinkSpec(
                sink=sys.stdout,
                format="{message}",
                level="INFO",
            )
        )

    if logfile is not None:
        sink_specs.append(
            _LogSinkSpec(
                sink=logfile,
                format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
                level="INFO",
                catch=True,
            )
        )

    return sink_specs
