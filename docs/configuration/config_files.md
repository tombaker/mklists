# Configuration files

`mklists` is configured through YAML files. Which file is read depends on the structure of the working directory.

## mklists.yaml

`mklists.yaml` is the configuration file for a **datatree** — a set of data directories under a common root. It is placed in the datatree root alongside `mklists.rules`.

When `mklists run` is invoked from a datadir within a datatree, configuration is read from `mklists.yaml` in the datatree root.

## .mklistsrc

`.mklistsrc` is the configuration file for a **self-contained datadir** — a single data directory processed independently, without reference to any datatree. It is placed inside the datadir alongside `.rules`.

When `.mklistsrc` is present, the datadir is treated as self-contained: any `mklists.yaml` in a parent directory is ignored.

Both files use the same YAML format and support the same set of keys.

## Config keys

### verbose

```yaml
verbose: true
```

Print progress messages during processing. Defaults to `true`.

### backup

```yaml
backup:
  backup_rootdir: null   # set to a name or absolute path to enable
  backup_depth: 3
```

`backup_rootdir` — directory where timestamped snapshots are written before each pass. A plain name (e.g. `.backups`) is resolved relative to the config file's directory. Set to `null` to disable backup (the default).

`backup_depth` — number of past backup snapshots to retain. Older snapshots are pruned after each run. Defaults to `3`.

### linkify

See [Linkify](linkify.md).

### routing

```yaml
routing:
  routing_dict: {}
```

Maps output filenames to destination directories. After each pass, any newly written file whose name appears as a key is moved to the corresponding directory. A plain directory name is resolved relative to the config file's directory; an absolute path is used as-is. An empty mapping (the default) disables routing.

Example:

```yaml
routing:
  routing_dict:
    to_inbox.txt: inbox        # sibling directory within the datatree
    to_archive.txt: /data/arc  # absolute path outside the datatree
```

### safety

```yaml
safety:
  invalid_filename_patterns:
    - \.swp$
    - \.tmp$
    - \.vim$
    - "~$"
```

List of regular expressions. Processing halts if any data file's name matches one of these patterns. The defaults catch common editor temporary files.

## Path resolution

Relative paths in `backup_rootdir`, `linkify_md_dir`, and `linkify_html_dir` are resolved relative to the **config file's directory** — the datatree root for `mklists.yaml`, or the datadir itself for `.mklistsrc`.

## Unknown keys

If a config file contains a key not recognized by `mklists`, processing halts with an error. Close matches are suggested in the error message.
