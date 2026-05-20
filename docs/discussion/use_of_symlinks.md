# Symlink behavior in mklists

## Setup

Suppose a datatree root exists at `/path/to/a/` containing `mklists.yaml` and
`mklists.rules`, and a datadir exists at `/path/to/b/datadir/` containing
`.rules`. The datadir is symlinked into the datatree root:

```
/path/to/a/datadir/ -> /path/to/b/datadir/
```

## Scenario 1 — running from inside the symlinked datadir

```
cd /path/to/a/datadir/
mklists run
```

`resolve_structural_context` (line 31 of `structure/resolve.py`) immediately
calls `Path(startdir).resolve()`, which follows symlinks. The working directory
`/path/to/a/datadir/` resolves to `/path/to/b/datadir/` before any other logic
runs.

`_resolve_startdir_context` then looks for `mklists.yaml` and `mklists.rules`
inside `/path/to/b/datadir/`. Neither exists there. Only `.rules` is found, so
mklists treats the directory as a **standalone datadir with no datatree root**.
The shared `mklists.rules` in `/path/to/a/` is never found or used.

**Result**: the symlink severs the datadir from its datatree root.

## Scenario 2 — running from the datatree root

```
cd /path/to/a/
mklists run
```

`_find_datadirs` calls `Path.iterdir()` on `/path/to/a/`. Python's `iterdir()`
yields symlink entries as-is without resolving them. The subsequent
`entry.is_dir()` and `(entry / ".rules").is_file()` calls do follow symlinks,
so `/path/to/a/datadir/` is recognised as a directory containing `.rules`.
mklists includes it as a normal datadir and processes it.

**Result**: the symlink is transparent; the datadir is detected and processed.

## Summary

| Starting point | Symlink visible? | Datatree root detected? |
|---|---|---|
| `/path/to/a/` (datatree root) | yes — `iterdir()` follows symlinks | yes |
| `/path/to/a/datadir/` (inside symlink) | n/a | no — `resolve()` strips the apparent parent |

The asymmetry comes entirely from the `Path.resolve()` call on line 31 of
`structure/resolve.py`. When descending from the root, symlinks are followed
transparently. When starting inside a symlinked directory, `resolve()` produces
the real path, discarding the directory's apparent location in the tree and
losing the datatree context with it.

## Decision

Symlinked datadirs are a feature, not an edge case. Tools such as mkdocs
support the same pattern without issue. mklists processes files by name via
ordinary OS calls that follow symlinks automatically, so there is no benefit to
resolving symlinks at the path level — and doing so actively breaks the case
where a symlinked datadir should inherit its datatree root from its apparent
parent.

The fix is to replace `Path(startdir).resolve()` with `Path(startdir).absolute()`
on line 31 of `structure/resolve.py`. `absolute()` makes relative paths
absolute and normalizes `..` components without following symlinks, which is the
correct semantics for a tool that works with directory trees by name rather than
by inode.

`Path.resolve()` follows symlinks and returns the physical filesystem path; `Path.absolute()` returns the logical path as given, made absolute, leaving symlinks in place.
