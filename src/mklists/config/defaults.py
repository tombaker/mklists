"""Default configuration settings in YAML."""


DEFAULT_CONFIG_YAML = """\
verbose: True

# Backup: snapshot data directories to a time-stamped directory before each pass.
# Set backup_rootdir (name or absolute path) to enable; null disables backup.
backup:
  backup_depth: 3
  backup_rootdir: null
  # backup_rootdir: .backups           # good for single, self-contained datadirs
  # backup_rootdir: /path/to/backups

# Linkify: write data files as HTML-in-Markdown (.md) to a browsable directory.
# Set linkify_dir (name or absolute path) to enable; null disables linkify.
linkify:
  linkify_dir: null
  # linkify_dir: .linkify             # good for single, self-contained datadirs
  # linkify_rootdir: /path/to/htmldir

# Routing: move newly generated files with special names to other directories.
# Populate routing_dict to enable; an empty mapping disables routing.
routing:
  routing_dict: {}
  # routing_dict:
  #   to_a.txt: a                  # for re-routing within datatree
  #   to_b.txt: b
  #   to_bar.txt: /Users/foo/bar   # for moving files out of datatree

# Safety: processing halts if safety criteria are violated.
safety:
  invalid_filename_patterns:
   - \\.swp$
   - \\.tmp$
   - \\.vim$
   - "~$"
"""
