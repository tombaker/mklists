Usage: mklists init datadir [OPTIONS] [PATH]

  Initialize a new mklists datadir (with its own rules).

  Creates `.rules` with commented example content. Pass `--bare` to create
  empty marker files instead.

  When run without `--self-contained`, prints paths of any datatree config
  files (`mklists.yaml`, `mklists.rules`) found in the parent directory.

Options:
  --bare            Create empty marker files with no example content.
  --self-contained  Write .mklistsrc, marking the datadir as self-contained.
  --help            Show this message and exit.
