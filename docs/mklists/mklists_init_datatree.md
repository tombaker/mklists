```
Usage: mklists init datatree [OPTIONS] [PATH]

  Initialize a new datatree.

  A datatree is a set of datadirs under a common root directory that
  potentially share rules (`mklists.rules`) and/or configuration settings
  (`mklists.yaml`).

  By default, `mklists init datatree` creates `mklists.yaml` and
  `mklists.rules` with commented example content.

  Datadirs are created in the datatree with `mklists init datatree`.

Options:
  --help  Show this message and exit.

Date: 2026-05-20
```
`mklists.yaml` is always written with `DEFAULT_CONFIG_YAML`.
`mklists.rules` is always written with `EXAMPLE_RULES`.
