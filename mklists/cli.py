"""CLI - command-line interface module"""

import click

# pylint: disable=unused-argument
#         During development, unused arguments here.


@click.group()
@click.version_option("0.2", help="Show version and exit")
@click.help_option(help="Show help and exit")
@click.pass_context
def cli(config):
    """Sync your lists to evolving rules."""
    # ctx.obj = get_configdict()
    #     verbose
    #     backup_depth
    #     htmlify
    #     invalid_filename_patterns
    #     files2dirs_dict


@cli.command()
@click.option("--bare", is_flag=True, help="Write minimal rule file.")
@click.argument("directory", type=click.Path(exists=False), nargs=-1)
@click.help_option(help="Show help and exit")
@click.pass_context
def init(config, directory):
    """Initialize list repo."""
    # if directory:
    #     os.chdir(Path(directory).resolve())
    # write_starter_configfile()
    # if bare:
    #     write_minimal_rulefiles()
    # else:
    #     write_starter_rulefiles()
    #     write_starter_datafile(datadir="lists")


@cli.command()
@click.option("--dryrun", is_flag=True, help="Run verbosely in read-only mode")
@click.option("--here-below", is_flag=True, help="Sync cwd and below (the default)")
@click.option("--here-only", is_flag=True, help="Sync cwd only")
@click.option("--everywhere", is_flag=True, help="Sync all data directories in repo")
@click.help_option(help="Show help and exit")
@click.pass_context
def sync(config, dryrun, here_below, here_only, everywhere):
    """Rebuild lists, by default in current directory and below"""

    # Scope of sync
    # if here-below: # default
    #     scope = get_datadir_paths_below(Path.cwd())
    # if everywhere:
    #     scope = get_datadir_paths_below(rootdir)
    # if here-only:
    #     scope = [Path.cwd()]

    # for dir in scope:
    #     # Read rule files from current and parent directories
    #     ruleobjs = get_rules()
    #
    #     # Get data lines from visible text files in (by default) current directory
    #     datalines = get_datalines(bad_filename_patterns)
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

    #     # Move specified files elsewhere (if desired)
    #     if ctx.obj["files2dirs_dict"]:
    #         move_specified_datafiles_elsewhere(files2dirs_dict)
