```
Usage: mklists init datadir [OPTIONS] [PATH]

  Initialize a new datadir.

  By default, creates a `.rules` file with commented example content.

Options:
  --bare            Create empty marker files with no example content.
  --self-contained  Write .mklistsrc, marking the datadir as self-contained.
  --help            Show this message and exit.

Date: 2026-05-20
```
| Command | `.rules` | `.mklistsrc` | parent check |
|---|---|---|---|
| `init datadir` | `EXAMPLE_RULES` | not created | yes |
| `init datadir --bare` | empty | not created | yes |
| `init datadir --self-contained` | `EXAMPLE_RULES` | `DEFAULT_CONFIG_YAML` | no |
| `init datadir --self-contained --bare` | empty | empty | no |

When run without `--self-contained`, mklists checks the parent directory for
datatree config files (`mklists.yaml`, `mklists.rules`) and prints the paths of
whichever exist. This helps orient the user when initializing a datadir inside
an existing datatree root. 

If neither `mklists.yaml` nor `mklists.rules` are found in its parent directory,
this means that the datadir is potentially part of a datatree but the datatree
has itself not yet been configured. While this is perfectly legal, it was possibly 
unintended, so mklists prints:
```
Warning: no mklists.yaml or mklists.rules found in parent directory (/path/to/datadir).
```
