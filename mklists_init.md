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
| `.mklistsrc` | `--self-contained` flag (marks datadir as self-contained) |

A self-contained datadir carries its own config. `.mklistsrc` may be empty
but its presence signals that intent.

### datatree mode

| File | Created when |
|---|---|
| `a/` and `b/` subdirs | Always |
| `a/.rules` | Always (empty — structural invariant for each datadir) |
| `b/.rules` | Always (empty — structural invariant for each datadir) |
| `mklists.yaml` | Always (empty — marker identifying the datatree root) |
| `mklists.rules` | Always (empty — shows users where shared rules go) |

Neither `mklists.yaml` nor `mklists.rules` is required by the engine for
a valid datatree, but both are created unconditionally: `mklists.yaml` as
a recognisable marker for conflict detection and users, `mklists.rules` as
a self-documenting placeholder showing where shared rules belong. Their
presence does no harm and costs nothing.

Every datadir must have a `.rules` file. `mklists init` always creates
these as empty markers. The `--rules` flag (datadir mode) populates `.rules`
with commented example content instead of leaving it empty.

## Flags

| Flag | Applies to | Effect |
|---|---|---|
| `--rules` | Both | Populate rule file(s) with commented example content |
| `--self-contained` | datadir only | Write `.mklistsrc`, marking the datadir as self-contained |
| `--subdirs TEXT` | datatree only | Comma-separated subdir names (default: `a,b`) |

`--rules` and `--self-contained` are init-time flags only. Running
`mklists init` a second time will hit the "never overwrite" invariant
and abort. Users who want example content after the fact should consult
the documentation.

Sample data has been deliberately excluded. Users can create their own
data files; generating sample data inside `mklists init` is conceptually
fraught and unnecessary.

## Hard invariant: never overwrite

Existing rule files and config files are never overwritten. If a conflict is
detected, the command aborts with a clear error message naming the conflicting
file. This is not a flag — it is unconditional.

## Error detection: mode markers and cross-mode conflicts

The following files act as mode markers:

- `.rules` in a directory → this directory is already a datadir
- `.mklistsrc` in a directory → this directory is already a self-contained datadir
- `mklists.yaml` or `mklists.rules` in a directory → this directory is already a datatree root

`mklists init` checks for all conflicts before writing anything
(all-or-nothing semantics):

| Command | Abort condition |
|---|---|
| `init datadir PATH` | `.rules` already exists in PATH |
| `init datadir PATH` | `.mklistsrc` already exists in PATH |
| `init datadir PATH` | `mklists.yaml` or `mklists.rules` exists in PATH |
| `init datatree PATH` | `.rules` already exists in PATH |
| `init datatree PATH` | `.mklistsrc` already exists in PATH |
| `init datatree PATH` | `mklists.yaml` or `mklists.rules` already exists in PATH |
| `init datatree PATH` | Any named subdir (`a`, `b`) already exists in PATH |

Each abort produces an informative error message identifying the conflicting
file or directory.

## What to avoid: interactive prompts

`sphinx-quickstart`-style interactive prompts are noisy and hostile to
scripting. `mklists init` should be purely flag-driven.

## Full CLI surface (sketch)

```
mklists init                              # shows help / usage error
mklists init datadir [PATH]               # initialize a single datadir
mklists init datatree [PATH]              # initialize a datatree with subdirs

Options for datadir:
  --rules            Populate .rules with commented example content
  --self-contained   Write .mklistsrc, marking the datadir as self-contained

Options for datatree:
  --rules            Populate all rule files (mklists.rules, a/.rules, b/.rules)
                     with commented example content
  --subdirs TEXT     Comma-separated subdir names [default: a,b]
```
