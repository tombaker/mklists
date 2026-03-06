"""Default configuration settings in YAML."""


DEFAULT_CONFIG_YAML = """\
verbose: False

# Backup: Snapshot data directory for each pass to a time-stamped backup directory.
backup:
  backup_enabled: False
  backup_rootdir: backups
  backup_depth: 3

# Linkification: After processing, data files can be written in HTML to given directory.
linkify:
  linkify_enabled: False
  linkify_dir: markdown

# Routing: Newly generated files with special names can be moved to given directories.
routing:
  routing_enabled: False
  routing_dict:
    to_a.txt: a
    to_b.txt: b
    to_bar.txt: /Users/foo/bar

# Safety: Processing halts if safety criteria are violated.
safety:
  invalid_filename_patterns:
   - \\.swp$
   - \\.tmp$
   - \\.vim$
   - "~$"
"""
