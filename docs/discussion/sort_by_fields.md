# Multi-key sort: design analysis

## Problem

The current sort key (fifth rule field) accepts a single integer that sorts by
"field N through end of line."  This means all lines dispatched to a target
file are sorted by one key only, and fields that carry type information (e.g.
`bookmark` vs `filehandle` in field 1) cannot be used as a primary group.

Concretely: with `sortkey=3`, lines whose field 3 (a file path) falls under the
same directory are interleaved regardless of their field-1 type:

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

## Proposed rule syntax

The fifth field accepts a comma-separated list of sort-key specs.  Each spec is
a field number (1-based, 0 = whole line) optionally followed by one or more
single-character modifiers:

```
3           →  sort by field 3, ascending          (backward-compatible)
1,3         →  primary field 1, secondary field 3
1r,3        →  primary field 1 descending, secondary field 3 ascending
1f,3n       →  primary field 1 case-insensitive, secondary field 3 numeric
```

The rule for the workspaces example becomes:

```
3|tbaker.Dropbox.WORKSPACES|tbaker_dropbox|tbaker_dropbox_workspaces|1,3
```

---

## Supported modifiers

| Modifier | Meaning | Implementation |
|---|---|---|
| `r` | Reverse (descending) | Flip comparison sign in the comparator |
| `n` | Numeric | Compare as `float`; fall back to string on `ValueError` |
| `f` | Fold case (case-insensitive) | Apply `str.casefold()` to the field value before comparing |

Modifiers may be combined: `1fr` = field 1, case-insensitive, descending.

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

The current behavior of a single integer `N` sorts by
`" ".join(fields[N-1:])` — field N concatenated with all trailing fields, so
they act as implicit tiebreakers.

Under the new design, `N` (as a single-element sort spec) sorts on exact field
N only.  Rules that happen to rely on trailing fields for tiebreaking will
produce different output.

In practice this matters only when field N is non-unique and the trailing fields
previously determined the final order.  The fix is to make the tiebreaker
explicit: `N,N+1` etc.

---

## Files to change

| File | Change |
|---|---|
| `rules/model.py` | Add `SortKey` dataclass (`field: int`, `reverse: bool`, `numeric: bool`, `casefold: bool`); replace `Rule.target_sortkey: int \| None` with `Rule.target_sortkeys: list[SortKey] \| None` |
| `rules/load.py` | Update `_parse_rule` to parse comma-separated sort specs with modifier suffixes |
| `exec/process_datalines.py` | Replace `_sort_datalines` with a `functools.cmp_to_key` comparator that iterates over `SortKey` list |
| `tests/rules/` and `tests/exec/` | Update and extend tests accordingly |

---

## Implementation sketch

```python
# rules/model.py
@dataclass(frozen=True)
class SortKey:
    field: int
    reverse: bool = False
    numeric: bool = False
    casefold: bool = False

# exec/process_datalines.py
import functools

def _sort_datalines(datalines: list[str], sortkeys: list[SortKey] | None) -> list[str]:
    if sortkeys is None:
        return datalines

    def compare(a: str, b: str) -> int:
        af, bf = a.split(), b.split()
        for sk in sortkeys:
            if sk.field == 0:
                av, bv = a, b
            else:
                idx = sk.field - 1
                av = af[idx] if idx < len(af) else ""
                bv = bf[idx] if idx < len(bf) else ""
            if sk.casefold:
                av, bv = av.casefold(), bv.casefold()
            if sk.numeric:
                try:
                    av_cmp: float | str = float(av)
                    bv_cmp: float | str = float(bv)
                except ValueError:
                    av_cmp, bv_cmp = av, bv
            else:
                av_cmp, bv_cmp = av, bv
            if av_cmp < bv_cmp:
                return 1 if sk.reverse else -1
            if av_cmp > bv_cmp:
                return -1 if sk.reverse else 1
        return 0

    return sorted(datalines, key=functools.cmp_to_key(compare))
```
