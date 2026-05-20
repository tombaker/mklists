# mklists init

## mklists init datadir

Initializes a standalone datadir — a directory with its own `.rules` file that
mklists uses as a structural marker and rule source.

By default both files are written with commented example content. Pass `--bare`
to suppress example content and create empty files instead.

When run without `--self-contained`, mklists checks the parent directory for
datatree config files (`mklists.yaml`, `mklists.rules`) and prints the paths of
whichever exist. This helps orient the user when initializing a datadir inside
an existing datatree root. If neither file is found, a warning is printed instead.

| Command | `.rules` | `.mklistsrc` | parent check |
|---|---|---|---|
| `init datadir` | `EXAMPLE_RULES` | not created | yes |
| `init datadir --bare` | empty | not created | yes |
| `init datadir --self-contained` | `EXAMPLE_RULES` | `DEFAULT_CONFIG_YAML` | no |
| `init datadir --self-contained --bare` | empty | empty | no |

## mklists init datatree

Initializes a datatree root — a directory with a shared `mklists.yaml` config
file and a shared `mklists.rules` rules file. No datadir subdirectories are
created. After writing the two files, mklists prints an advisory message
directing the user to create datadirs with `mklists init datadir`.

`mklists.yaml` is always written with `DEFAULT_CONFIG_YAML`.
`mklists.rules` is always written with `EXAMPLE_RULES`.

| Command | `mklists.yaml` | `mklists.rules` | datadirs |
|---|---|---|---|
| `init datatree` | `DEFAULT_CONFIG_YAML` | `EXAMPLE_RULES` | none; advisory message shown |
