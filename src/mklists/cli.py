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
    help="Show status as if started in <path> instead of current directory.",
)
def status(directory: str | None) -> None:
    """Show current directory's mklists structural context and configuration."""
    startdir = Path(directory).resolve() if directory else Path.cwd()
    try:
        structural_context = resolve_structural_context(startdir)
    except MklistsError as e:
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

    click.echo(f"Directory : {sc.startdir}")
    click.echo(f"Role      : {role}")
    click.echo(f"Datadirs  : {datadir_names or '(none)'}")
    click.echo("")
    click.echo("Marker files:")
    click.echo(f"  mklists.yaml  : {found(sc.datatree_configfile_found)}")
    click.echo(f"  mklists.rules : {found(sc.datatree_rulefile_found)}")
    click.echo(f"  .rules        : {found(sc.datadir_rulefile_found)}")
    click.echo(f"  .mklistsrc    : {found(sc.datadir_configfile_found)}")

    try:
        config = resolve_config(structural_context)
    except MklistsError as e:
        raise click.ClickException(str(e)) from e

    def show(path: object) -> str:
        return str(path) if path is not None else "not set"

    routing_lines = config.routing.routing_dict
    if routing_lines:
        routing_str = ", ".join(f"{k} -> {v}" for k, v in sorted(routing_lines.items()))
    else:
        routing_str = "none"

    safety_patterns = config.safety.invalid_filename_patterns
    if safety_patterns:
        safety_str = ", ".join(p.pattern for p in safety_patterns)
    else:
        safety_str = "none"

    click.echo("")
    click.echo("Config:")
    click.echo(f"  Config file      : {show(config.configfile_used)}")
    click.echo(f"  Verbose          : {config.verbose}")
    click.echo(f"  Backup dir       : {show(config.backup.backup_rootdir)}")
    click.echo(f"  Backup depth     : {config.backup.backup_depth}")
    click.echo(f"  Linkify MD dir   : {show(config.linkify.linkify_md_dir)}")
    click.echo(f"  Linkify HTML dir : {show(config.linkify.linkify_html_dir)}")
    click.echo(f"  Routing          : {routing_str}")
    click.echo(f"  Safety patterns  : {safety_str}")


@cli.command()
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
        config = resolve_config(structural_context)
        init_logger(logfile=None, verbose=config.verbose)
        run_plan = resolve_run_plan(
            structural_context=structural_context, config=config
        )
        run_mklists(run_plan)
    except MklistsError as e:
        raise click.ClickException(str(e)) from e
