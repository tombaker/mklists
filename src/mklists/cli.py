"""CLI entry point for mklists."""

import click


@click.group()
def cli() -> None:
    """Rules-based file transformation tool."""


@cli.command()
def init() -> None:
    """Initialize a mklists repository in the current directory."""
    click.echo("Running mklists init.")


@cli.command()
def run() -> None:
    """Run mklists against the current directory."""
    click.echo("Running mklists run.")
