"""CLI entry point for mklists."""

from pathlib import Path

import click

from mklists.config.resolve import resolve_config
from mklists.errors import MklistsError
from mklists.exec.run import run_mklists
from mklists.plan.resolve import resolve_run_plan
from mklists.structure.resolve import resolve_structural_context


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
    """Initialize a new mklists datatree or datadir (data directory)."""
    ctx.ensure_object(dict)
    ctx.obj["directory"] = directory
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@init.command()
@click.pass_context
def datatree(_ctx: click.Context) -> None:
    """Initialize a new mklists datatree (where datadirs share rules)."""
    click.echo("Running mklists init datatree.")


@init.command()
@click.pass_context
def datadir(_ctx: click.Context) -> None:
    """Initialize new datadir (with own rules)."""
    click.echo("Running mklists init datadir.")


@cli.command()
@click.option(
    "-C",
    "directory",
    default=None,
    metavar="<path>",
    help="Run as if started in <path> instead of current directory.",
)
def run(directory: str | None) -> None:
    """Run mklists against the current directory."""
    startdir = Path(directory).resolve() if directory else Path.cwd()
    try:
        structural_context = resolve_structural_context(startdir)
        config = resolve_config(structural_context)
        run_plan = resolve_run_plan(structural_context=structural_context, config=config)
        run_mklists(run_plan)
    except MklistsError as e:
        raise click.ClickException(str(e)) from e
