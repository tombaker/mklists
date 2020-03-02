"""CLI - command-line interface module"""

import os
from pathlib import Path
import click
from .apply import (  # noqa: F401
    apply_rules_to_datalines,
    find_data_subdir_paths,
    get_configdict,
    get_datalines,
    move_specified_datafiles_elsewhere,
    write_new_datafiles,
)
from .backup import move_datafiles_to_backupdir, delete_older_backupdirs  # noqa: F401
from .config import (  # noqa: F401
    write_starter_configfile,
    write_minimal_rulefiles,
    write_starter_rulefiles,
    write_starter_datafile,
)
from .linkify import write_htmlfiles  # noqa: F401
from .rules import Rule, get_rules  # noqa: F401

# pylint: disable=unused-argument
#         During development, unused arguments here.


@click.group()
@click.version_option("0.2", help="Show version and exit")
@click.help_option(help="Show help and exit")
@click.pass_context
def cli(config):
    """Sync your lists to evolving rules."""
    # ctx.obj = get_configdict()
    #     verbose = ctx.obj["verbose"]
    #     backups = ctx.obj["backup_depth"]
    #     will_linkify = ctx.obj["linkify"]
    #     fname_patterns = ctx.obj["invalid_filename_patterns"]
    #     files2dirs = ctx.obj["files2dirs_dict"]
    #     pathstems = ctx.obj["pathstem_list"]


@cli.command()
@click.argument("directory", type=click.Path(exists=False), nargs=1, required=False)
@click.option("--bare", is_flag=True, help="Write minimal rule file.")
@click.help_option(help="Show help and exit")
@click.pass_context
def init(config, directory, bare):
    """Initialize list repo."""
    print(f"config: {config}")
    print(f"directory: {directory}")
    print(f"bare: {bare}")
    if directory:
        os.mkdir(Path(directory).resolve())
        os.chdir(directory)
    write_starter_configfile()
    if bare:
        write_minimal_rulefiles()
    else:
        write_starter_rulefiles()
        write_starter_datafile()


@cli.command()
@click.option("--dryrun", is_flag=True, help="Run verbosely in read-only mode")
@click.option("--here-only", is_flag=True, help="Sync cwd only (the default)")
@click.option("--here-subdirs", is_flag=True, help="Sync cwd and directories below")
@click.option("--root-subdirs", is_flag=True, help="Sync all data directories in repo")
@click.help_option(help="Show help and exit")
@click.pass_context
def sync(config, dryrun, here_subdirs, here_only, root_subdirs):
    """Rebuild lists, by default in current directory and subdirs"""

    # Scope of sync
    # if here_only:    # default
    #     scope = [Path.cwd()]
    # if here_subdirs:
    #     scope = find_data_subdir_paths(Path.cwd())
    # if root_subdirs:
    #     scope = find_data_subdir_paths(rootdir)

    # for dir in scope:
    #     os.chdir(dir)
    #     # Read rule files from current and parent directories
    #     ruleobjs = get_rules()
    #
    #     # Get data lines from visible text files in (by default) current directory
    #     datalines = get_datalines(invalid_filename_patterns)
    #     filenames2lines_dict = apply_rules_to_datalines(ruleobjs, datalines)
    #
    #     # Move existing data files to timestamped subdirectory of _backups/
    #     # If backup_depth is set to 0, existing data files simply deleted (careful!)
    #     if ctx.obj["backup_depth"]:
    #         move_datafiles_to_backupdir()
    #         delete_older_backupdirs(backup_depth)

    #     # Write out new datafiles:
    #     write_new_datafiles(filenames2lines_dict)

    #     # Write out "linkified" files to subdirectory of _html/ (if desired)
    #     if ctx.obj["linkify"]:
    #         write_htmlfiles(filenames2lines_dict)

    #     # Move specified files elsewhere (as specified and if desired)
    #     if ctx.obj["files2dirs_dict"]:
    #         move_specified_datafiles_elsewhere(files2dirs_dict)
