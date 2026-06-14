# Multi-key sort

## Problem

The original sort key (fifth rule field) accepted a single integer that sorted
by "field N through end of line."  This meant all lines dispatched to a target
file were sorted by one key only, so fields that carry type information (e.g.
`bookmark` vs `filehandle` in field 1) could not be used as a primary group.

Concretely: with `sortkey=3`, lines whose field 3 (a file path) falls under the
same directory were interleaved regardless of their field-1 type:

```
bookmark CTRB      /Users/tbaker/Dropbox/WORKSPACES/CTRB
filehandle :Ctrb   /Users/tbaker/Dropbox/WORKSPACES/CTRB/index.md
bookmark FLATSRAP  /Users/tbaker/Dropbox/WORKSPACES/FLATSRAP
filehandle :Flatsrap /Users/tbaker/Dropbox/WORKSPACES/FLATSRAP/index.md
```

The desired output groups by type first, then by path:

```
bookmark CTRB      /Users/tbaker/Dropbox/WORKSPACES/CTRB
bookmark FLATSRAP  /Users/tbaker/Dropbox/WORKSPACES/FLATSRAP
...
filehandle :Ctrb   /Users/tbaker/Dropbox/WORKSPACES/CTRB/index.md
filehandle :Flatsrap /Users/tbaker/Dropbox/WORKSPACES/FLATSRAP/index.md
```

---

## Rule syntax

The fifth field accepts a comma-separated list of sort-key specs.  Each spec is
a field number (1-based; 0 = whole line) optionally followed by one or more
single-character modifiers:

```
3           →  sort by field 3, ascending          (backward-compatible)
1,3         →  primary field 1, secondary field 3
1r,3        →  primary field 1 descending, secondary field 3 ascending
1f,3n       →  primary field 1 case-insensitive, secondary field 3 numeric
```

Whitespace around commas and specs is ignored: `1, 3` is identical to `1,3`.

The rule for the workspaces example:

```
3|tbaker.Dropbox.WORKSPACES|tbaker_dropbox|tbaker_dropbox_workspaces|1,3
```

---

## Supported modifiers

| Modifier | Meaning | Implementation |
|---|---|---|
| `r` | Reverse (descending) | Flip comparison sign in the comparator |
| `n` | Numeric | Compare as `float`; fall back to string comparison on `ValueError` |
| `f` | Fold case (case-insensitive) | Apply `str.casefold()` to the field value before comparing |

Modifiers may be combined on a single spec: `2rn` = field 2, numeric,
descending.  Order of modifier letters within a spec does not matter.

### Why not other Unix `sort` modifiers

| Modifier | Reason excluded |
|---|---|
| `b` (ignore leading blanks) | Fields are already split on whitespace; leading blanks cannot survive |
| `i` (ignore non-printable) | mklists data is plain text; this is a no-op in practice |
| `d` (dictionary order) | Niche; adds complexity for minimal benefit |
| `M` (month names) | Too domain-specific |
| `h` (human-readable numbers) | Too domain-specific |
| `V` (version sort) | Complex; not a current need |

---

## Breaking change

The original behavior of a single integer `N` sorted by
`" ".join(fields[N-1:])` — field N concatenated with all trailing fields, so
they acted as implicit tiebreakers.

Under the new design, `N` (as a single-element sort spec) sorts on exact field
N only.  Rules that relied on trailing fields for tiebreaking will produce
different output.

In practice this matters only when field N is non-unique and the trailing fields
previously determined the final order.  The fix is to make the tiebreaker
explicit: `N,N+1` etc.

---

## Implementation

- `rules/model.py` — `SortKey` dataclass (`field: int`, `reverse: bool`,
  `numeric: bool`, `casefold: bool`); `Rule.target_sortkeys: list[SortKey] | None`
- `rules/load.py` — `_parse_sort_spec` parses one spec; `_parse_rule` splits
  the fifth field on commas and produces a `list[SortKey]`
- `exec/process_datalines.py` — `_sort_datalines` uses `functools.cmp_to_key`
  with a comparator that iterates over the `SortKey` list
