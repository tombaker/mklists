# Design notes: `mklists init`

## Mode selection: subcommands, not flags

`mklists init` alone shows help text — no default mode.
The user must specify one of:

```
mklists init datadir  [PATH]
mklists init datatree [PATH]
```

The two modes produce structurally different results (flat directory vs. tree
with subdirectories, different file names), so they are genuinely distinct
operations rather than variations of one operation. Subcommands make that
distinction explicit.

`PATH` defaults to `.` (current working directory), matching the convention
established by `git init [directory]`.

## Files created

### datadir mode

| File | Created when |
|---|---|
| `.rules` | Always (empty — structural invariant) |
| `.mklistsrc` | `--config` flag |

### datatree mode

| File | Created when |
|---|---|
| `a/` and `b/` | Always (subdirectory structure) |
| `mklists.rules` | Always (empty — structural invariant for datatree root) |
| `a/.rules` | Always (empty — structural invariant for each datadir) |
| `b/.rules` | Always (empty — structural invariant for each datadir) |
| `mklists.yaml` | `--config` flag |

Every datadir must have a `.rules` file. `mklists init` always creates it as an
empty marker, unconditionally. The `--rules` flag populates it with commented
example content for users who want a template to edit.

## Flags

| Flag | Applies to | Effect |
|---|---|---|
| `--rules` | Both | Populate rule file(s) with commented example content instead of leaving them empty |
| `--config` | Both | Write default config file |
| `--subdirs TEXT` | datatree only | Comma-separated subdir names (default: `a,b`) |

`--rules` and `--config` are init-time flags only. They do not support
post-init population: running `mklists init` a second time will hit the
"never overwrite" invariant and abort. Users who want example content after
the fact should consult the documentation.

Sample data (`--sample`) has been dropped from the design. Users can create
their own data files and consult documentation for examples. Generating sample
data inside `mklists init` is conceptually fraught and unnecessary.

## Hard invariant: never overwrite

Existing rule files and config files are never overwritten. If a conflict is
detected, the command aborts with a clear error message naming the conflicting
file. This is not a flag — it is unconditional.

## Error detection: mode markers and cross-mode conflicts

Certain files act as mode markers that signal an existing initialization:

- `.rules` in a directory → signals "this directory is already a datadir"
- `mklists.yaml` or `mklists.rules` in a directory → signals "this directory is already a datatree root"

`mklists init` checks for conflicts before writing anything:

| Command | Abort condition | Message |
|---|---|---|
| `init datadir PATH` | `.rules` already exists in PATH | Directory already initialized as a datadir |
| `init datadir PATH` | `mklists.yaml` or `mklists.rules` exists in PATH | Directory already initialized as a datatree root |
| `init datatree PATH` | `.rules` already exists in PATH | Directory already initialized as a datadir |
| `init datatree PATH` | `mklists.yaml` or `mklists.rules` already exists in PATH | Directory already initialized as a datatree root |
| `init datatree PATH` | Named subdir (`a`, `b`) already exists in PATH | Subdir conflict — abort with informative message |

All checks run before any files are written (all-or-nothing semantics).

## What to avoid: interactive prompts

`sphinx-quickstart`-style interactive prompts are noisy and hostile to
scripting. `mklists init` should be purely flag-driven.

## Full CLI surface (sketch)

```
mklists init                              # shows help / usage error
mklists init datadir [PATH]               # initialize a single datadir
mklists init datatree [PATH]              # initialize a datatree with subdirs

Options for datadir:
  --rules          Populate .rules with commented example content
  --config         Write default .mklistsrc

Options for datatree:
  --rules          Populate rule files with commented example content
  --config         Write default mklists.yaml
  --subdirs TEXT   Comma-separated subdir names [default: a,b]
```
