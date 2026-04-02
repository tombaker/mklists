"""CLI entry point for mklists."""

from pathlib import Path

import click

from mklists.config.resolve import resolve_config
from mklists.errors import MklistsError
from mklists.exec.run import run_mklists
from mklists.init.datadir import init_datadir
from mklists.init.datatree import init_datatree
from mklists.logging import init_logger
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
    """Initialize a new Mklists datatree or datadir.

    Running `mklists init` in an existing Mklists datatree or datadir
    is safe. It will not overwrite things that are already there.
    """
    ctx.ensure_object(dict)
    ctx.obj["directory"] = directory
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@init.command()
@click.argument("path", default=".", metavar="[PATH]")
@click.option(
    "--rules",
    is_flag=True,
    default=False,
    help="Populate rule files with commented example content.",
)
@click.option(
    "--subdirs",
    default="a,b",
    metavar="<names>",
    help="Comma-separated subdir names (default: a,b).",
)
@click.pass_context
def datatree(ctx: click.Context, path: str, rules: bool, subdirs: str) -> None:
    """Initialize a new mklists datatree (where datadirs share rules)."""
    directory = ctx.obj.get("directory")
    if directory is not None and path != ".":
        raise click.UsageError("-C and PATH are mutually exclusive.")
    if directory is not None:
        resolved = Path(directory).resolve()
    else:
        resolved = Path(path).resolve()
    subdir_tuple = tuple(s.strip() for s in subdirs.split(",") if s.strip())
    try:
        init_datatree(resolved, rules=rules, subdirs=subdir_tuple)
    except MklistsError as e:
        raise click.ClickException(str(e)) from e


@init.command()
@click.argument("path", default=".", metavar="[PATH]")
@click.option(
    "--rules",
    is_flag=True,
    default=False,
    help="Populate .rules with commented example content.",
)
@click.option(
    "--self-contained",
    is_flag=True,
    default=False,
    help="Write .mklistsrc, marking the datadir as self-contained.",
)
@click.pass_context
def datadir(ctx: click.Context, path: str, rules: bool, self_contained: bool) -> None:
    """Initialize a new mklists datadir (with its own rules)."""
    directory = ctx.obj.get("directory")
    if directory is not None and path != ".":
        raise click.UsageError("-C and PATH are mutually exclusive.")
    if directory is not None:
        resolved = Path(directory).resolve()
    else:
        resolved = Path(path).resolve()
    try:
        init_datadir(resolved, rules=rules, self_contained=self_contained)
    except MklistsError as e:
        raise click.ClickException(str(e)) from e


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
        init_logger(logfile=None, verbose=config.verbose)
        run_plan = resolve_run_plan(
            structural_context=structural_context, config=config
        )
        run_mklists(run_plan)
    except MklistsError as e:
        raise click.ClickException(str(e)) from e
