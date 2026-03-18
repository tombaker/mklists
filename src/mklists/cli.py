"""CLI entry point for mklists."""

import click


@click.group()
def cli() -> None:
    """Rule-based maintenance of plain-text lists."""


@cli.command()
def init() -> None:
    """Create Mklists repository in current directory."""
    click.echo("Running mklists init.")


@cli.command()
@click.option(
    "-C",
    "directory",
    default=None,
    metavar="<path>",
    help="Run as if started in <path> instead of current work tree.",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    default=False,
    help="Print only errors and warnings; suppress all else.",
)
def run(directory: str | None, quiet: bool) -> None:
    """Run mklists against the current directory."""
    click.echo("Running mklists run.")
