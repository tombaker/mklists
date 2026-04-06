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
@click.pass_context
def init(ctx: click.Context) -> None:
    """Initialize a new Mklists datatree or datadir."""
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
    "--datadirs",
    default=None,
    metavar="<names>",
    help="Comma-separated datadir names to create (default: a,b).",
)
@click.option(
    "--bare",
    is_flag=True,
    default=False,
    help="Create only mklists.yaml and mklists.rules; no datadirs.",
)
def datatree(path: str, rules: bool, datadirs: str | None, bare: bool) -> None:
    """Initialize a new mklists datatree (where datadirs share rules)."""
    if bare and datadirs is not None:
        raise click.UsageError("--bare and --datadirs are mutually exclusive.")
    resolved = Path(path).resolve()
    if bare:
        datadir_tuple: tuple[str, ...] = ()
    elif datadirs is not None:
        datadir_tuple = tuple(s.strip() for s in datadirs.split(",") if s.strip())
    else:
        datadir_tuple = ("a", "b")
    try:
        written = init_datatree(resolved, rules=rules, datadirs=datadir_tuple)
    except MklistsError as e:
        raise click.ClickException(str(e)) from e
    for file_path in written:
        click.echo(f"Wrote {file_path}")


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
def datadir(path: str, rules: bool, self_contained: bool) -> None:
    """Initialize a new mklists datadir (with its own rules)."""
    resolved = Path(path).resolve()
    try:
        written = init_datadir(resolved, rules=rules, self_contained=self_contained)
    except MklistsError as e:
        raise click.ClickException(str(e)) from e
    for file_path in written:
        click.echo(f"Wrote {file_path}")


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
