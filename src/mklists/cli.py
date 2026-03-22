"""CLI entry point for mklists."""

import click


@click.group()
def cli() -> None:
    """Rule-based maintenance of plain-text lists."""


@cli.group(invoke_without_command=True)
@click.option(
    "-C",
    "directory",
    default=None,
    metavar="<path>",
    help="Run as if started in <path> instead of current directory.",
)
@click.pass_context
def init(ctx: click.Context, directory: str | None) -> None:
    """Initialize a new mklists repo or data directory."""
    ctx.ensure_object(dict)
    ctx.obj["directory"] = directory
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@init.command()
@click.pass_context
def repo(ctx: click.Context) -> None:
    """Initialize a new mklists repository in the current directory."""
    click.echo("Running mklists init repo.")


@init.command()
@click.pass_context
def datadir(ctx: click.Context) -> None:
    """Initialize a new data directory in the current directory."""
    click.echo("Running mklists init datadir.")


@cli.command()
@click.option(
    "-C",
    "directory",
    default=None,
    metavar="<path>",
    help="Run as if started in <path> instead of current directory.",
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
