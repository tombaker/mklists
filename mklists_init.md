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

| File | Created by |
|---|---|
| `.rules` | `--rules` flag |
| `.mklistsrc` | `--config` flag |

### datatree mode

| File | Created by |
|---|---|
| `mklists.rules` | `--rules` flag |
| `a/.rules` | `--rules` flag |
| `b/.rules` | `--rules` flag |
| `mklists.yaml` | `--config` flag |

## Flags (both subcommands)

| Flag | Effect |
|---|---|
| `--rules` | Write default rule file(s) |
| `--config` | Write default config file |
| `--sample` | Populate directory with simple sample data |
| `--subdirs TEXT` | Comma-separated subdir names (datatree only; default: `a,b`) |

All flags are opt-in. No files are written by default beyond the minimum
directory structure.

## Hard invariant: never overwrite

Existing rule files and config files are never overwritten. If a conflict is
detected, the command aborts with a clear error message naming the conflicting
file. This is not a flag — it is unconditional.

## Rationale for opt-in defaults

Defaulting to writing no files (requiring explicit `--rules`, `--config`,
`--sample`) means the user must consciously choose what is created. This avoids
surprising new users with files they do not yet understand, and keeps the
command composable in scripts where only some files are wanted.

## What to avoid: interactive prompts

`sphinx-quickstart`-style interactive prompts are noisy and hostile to
scripting. `mklists init` should be purely flag-driven.

## Full CLI surface (sketch)

```
mklists init                              # shows help / usage error
mklists init datadir [PATH]               # initialize a single datadir
mklists init datatree [PATH]              # initialize a datatree with subdirs

Options (both subcommands):
  --rules          Write default rule file(s)
  --config         Write default config file
  --sample         Populate with sample data
  --subdirs TEXT   Comma-separated subdir names [datatree only; default: a,b]
```
