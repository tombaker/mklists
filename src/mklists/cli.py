"""CLI entry point for mklists."""

import datetime
from pathlib import Path

import click

from mklists.config.resolve import resolve_config
from mklists.errors import MklistsError, StructureError
from mklists.exec.run import run_mklists
from mklists.init.datadir import init_datadir
from mklists.init.datatree import init_datatree
from mklists.logging import init_logger
from mklists.plan.resolve import resolve_run_plan
from mklists.structure.markers import (
    DATADIR_CONFIGFILE_NAME,
    DATADIR_RULEFILE_NAME,
    DATATREE_CONFIGFILE_NAME,
    DATATREE_RULEFILE_NAME,
)
from mklists.structure.resolve import resolve_structural_context


def _write_date_epilog(formatter: click.HelpFormatter) -> None:
    formatter.write_paragraph()
    formatter.write(f"Date: {datetime.date.today().isoformat()}\n")


class _DateGroup(click.Group):
    def format_epilog(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        _write_date_epilog(formatter)


class _DateCommand(click.Command):
    def format_epilog(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        _write_date_epilog(formatter)


def _echo_startdir_context(startdir: Path) -> None:
    """Echo directory, role, and marker file presence for startdir."""

    def found(path: object) -> str:
        return str(path) if path is not None else "not found"

    def if_file_exists(p: Path) -> Path | None:
        return p if p.is_file() else None

    yaml = found(if_file_exists(startdir / DATATREE_CONFIGFILE_NAME))
    rules = found(if_file_exists(startdir / DATATREE_RULEFILE_NAME))
    dot_rules = found(if_file_exists(startdir / DATADIR_RULEFILE_NAME))
    dot_rc = found(if_file_exists(startdir / DATADIR_CONFIGFILE_NAME))
    click.echo(f"Directory : {startdir}")
    click.echo("Role      : unknown (neither datatree root nor datadir)")
    click.echo("Datadirs  : none in scope")
    click.echo("")
    click.echo("Datatree marker/config files:")
    click.echo(f"  mklists.yaml  : {yaml}")
    click.echo(f"  mklists.rules : {rules}")
    click.echo("")
    click.echo("Datadir marker/config files:")
    click.echo(f"  .rules        : {dot_rules}")
    click.echo(f"  .mklistsrc    : {dot_rc}")
    click.echo("")


@click.group(cls=_DateGroup)
def cli() -> None:
    """Rule-based maintenance of plain-text lists."""


@cli.group(cls=_DateGroup, invoke_without_command=True)
@click.pass_context
def init(ctx: click.Context) -> None:
    """Initialize a new datatree or datadir."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@init.command(cls=_DateCommand)
@click.argument("path", default=".", metavar="[PATH]")
def datatree(path: str) -> None:
    """Initialize a new datatree.

    A datatree is a set of datadirs under a common root directory that
    potentially share rules (`mklists.rules`) and/or configuration settings
    (`mklists.yaml`).

    By default, `mklists init datatree` creates `mklists.yaml` and 
    `mklists.rules` with commented example content.

    Datadirs are created in the datatree with `mklists init datatree`.
    """
    resolved = Path(path).resolve()
    try:
        written = init_datatree(resolved)
    except MklistsError as e:
        raise click.ClickException(str(e)) from e
    for file_path in written:
        click.echo(f"Wrote {file_path}")
    click.echo(
        "To add a datadir under this root, run: mklists init datadir <path>"
    )


@init.command(cls=_DateCommand)
@click.argument("path", default=".", metavar="[PATH]")
@click.option(
    "--bare",
    is_flag=True,
    default=False,
    help="Create empty marker files with no example content.",
)
@click.option(
    "--self-contained",
    is_flag=True,
    default=False,
    help="Write .mklistsrc, marking the datadir as self-contained.",
)
def datadir(path: str, bare: bool, self_contained: bool) -> None:
    """Initialize a new datadir.

    By default, creates a `.rules` file with commented example content.
    """
    resolved = Path(path).resolve()
    try:
        written = init_datadir(resolved, bare=bare, self_contained=self_contained)
    except MklistsError as e:
        raise click.ClickException(str(e)) from e
    for file_path in written:
        click.echo(f"Wrote {file_path}")
    if not self_contained:
        parent = resolved.parent
        found_in_parent = []
        for name in (DATATREE_CONFIGFILE_NAME, DATATREE_RULEFILE_NAME):
            candidate = parent / name
            if candidate.is_file():
                found_in_parent.append(candidate)
                click.echo(f"Found in parent: {candidate}")
        if not found_in_parent:
            click.echo(
                f"Warning: no {DATATREE_CONFIGFILE_NAME} or {DATATREE_RULEFILE_NAME}"
                f" found in parent directory ({parent})."
            )


@cli.command(cls=_DateCommand)
@click.option(
    "-C",
    "directory",
    default=None,
    metavar="<path>",
    help="Show status as if started in <path> instead of current directory.",
)
def status(directory: str | None) -> None:
    """Show current directory's mklists structural context and configuration."""
    startdir = Path(directory).resolve() if directory else Path.cwd()
    try:
        structural_context = resolve_structural_context(startdir)
    except StructureError as e:
        _echo_startdir_context(startdir)
        raise click.ClickException(str(e)) from e

    sc = structural_context.startdir_context

    if sc.is_datatree_root:
        role = "datatree root"
    elif sc.is_datadir_selfcontained:
        role = "self-contained datadir"
    else:
        role = "datadir (in datatree)"

    datadir_names = ", ".join(
        dc.datadir.name for dc in structural_context.datadir_contexts
    )

    def found(path: object) -> str:
        return str(path) if path is not None else "not found"

    def if_file_exists(p: Path) -> Path | None:
        return p if p.is_file() else None

    if sc.is_datadir_in_datatree:
        datatree_root = sc.config_rootdir
        datatree_configfile = if_file_exists(datatree_root / DATATREE_CONFIGFILE_NAME)
        datatree_rulefile = if_file_exists(datatree_root / DATATREE_RULEFILE_NAME)
    else:
        datatree_configfile = sc.datatree_configfile_found
        datatree_rulefile = sc.datatree_rulefile_found

    click.echo(f"Directory : {sc.startdir}")
    click.echo(f"Role      : {role}")
    click.echo(f"Datadirs  : {datadir_names or 'none'} in scope")
    click.echo("")
    click.echo("Datatree marker/config files:")
    click.echo(f"  mklists.yaml  : {found(datatree_configfile)}")
    click.echo(f"  mklists.rules : {found(datatree_rulefile)}")
    click.echo("")
    click.echo("Datadir marker/config files:")
    click.echo(f"  .rules        : {found(sc.datadir_rulefile_found)}")
    click.echo(f"  .mklistsrc    : {found(sc.datadir_configfile_found)}")

    try:
        config = resolve_config(structural_context)
    except MklistsError as e:
        raise click.ClickException(str(e)) from e

    def show(path: object) -> str:
        return str(path) if path is not None else "not set"

    click.echo("")
    click.echo("Config:")
    click.echo(f"  Config file      : {show(config.configfile_used)}")
    click.echo(f"  Backup dir       : {show(config.backup.backup_rootdir)}")
    click.echo(f"  Linkify MD dir   : {show(config.linkify.linkify_md_dir)}")
    click.echo(f"  Linkify HTML dir : {show(config.linkify.linkify_html_dir)}")


@cli.command(cls=_DateCommand)
@click.option(
    "-C",
    "directory",
    default=None,
    metavar="<path>",
    help="Run as if started in <path> instead of current directory.",
)
def run(directory: str | None) -> None:
    """Run mklists against current directory."""
    startdir = Path(directory).resolve() if directory else Path.cwd()
    try:
        structural_context = resolve_structural_context(startdir)
    except StructureError as e:
        _echo_startdir_context(startdir)
        raise click.ClickException(str(e)) from e
    try:
        config = resolve_config(structural_context)
        init_logger(logfile=None, verbose=config.verbose)
        run_plan = resolve_run_plan(
            structural_context=structural_context, config=config
        )
        empty_datadirs = run_mklists(run_plan)
    except MklistsError as e:
        raise click.ClickException(str(e)) from e
    for path in empty_datadirs:
        click.echo(f"No data found in {path}")
