# Sort order options for mklists

## Current state

The rule file's 5th field is a single integer parsed in `load.py:151`
(`int(raw_sortorder)`). The sort in `process_datalines.py:131` extracts one
whitespace-delimited field and sorts on that string alone. Fields beyond the
sort key are ignored, so ties are broken arbitrarily by Python's stable sort
(i.e., original list order).

## Options

### Option A — Sort from field N to end of line ("N+")

The sort key becomes `" ".join(fields[N-1:])`, i.e., the remainder of the line
starting at field N.

**Rule file syntax:** a trailing `+`, e.g., `3+` instead of `3`.

**What changes:**
- `_parse_rule` in `load.py`: detect and strip the `+` suffix, set a flag or a
  separate field on `Rule`
- `_sort_datalines` in `process_datalines.py`: join from field N onward instead
  of extracting one field
- `Rule` dataclass in `model.py`: either a boolean `sortkey_to_end: bool` or a
  convention like storing `None` for "no sort" and a negative integer for "from
  field N to end"

**Pros:** Solves the immediate problem with minimal code change. "From field 3
to end" naturally orders by field 3, then by field 4, then field 5, etc.  
**Cons:** No numeric sort, no non-contiguous key ordering (e.g., sort by field 5
then field 2).

---

### Option B — Comma-separated field list (`3,4` or `3,4,5`)

The sort key becomes a tuple `(field3_text, field4_text, ...)`, which Python
compares lexicographically.

**Rule file syntax:** comma-separated integers, e.g., `3,4`.

**What changes:**
- `_parse_rule`: split on commas, parse each as int, store as `list[int]`
- `Rule.target_sortkey`: change type from `int | None` to
  `int | list[int] | None`
- `_sort_datalines`: build a tuple key

**Pros:** Handles non-contiguous keys (sort by field 5 then field 2). Still
simple.  
**Cons:** No numeric sort. A minor type-union complication in `model.py` and
everywhere `target_sortkey` is used.

---

### Option C — Full `sort(1)`-style spec (`3,4n` or `3 4n` etc.)

Parse a mini-language like `sort -k 3,4 -k 4n,5` where:
- `n` = numeric comparison
- `r` = reverse
- start,end = field range (sort(1) semantics: start at field N, end *before*
  delimiter of field M)

**Rule file syntax:** a quoted string in field 5, e.g., `3,4 4n,5`.

**What changes:** significant. Need a spec parser, a key-function builder,
handling of `n`/`r` flags, and the rule file delimiter logic (field 5 currently
cannot contain spaces without changing the pipe-split logic — or allow the 5th
field to be everything after the 4th `|`).

**Note on `M` (month) sort:** Python has no native month-name sort; a lookup
table (`Jan`→1, `Feb`→2, …) would be needed. Doable but adds code.

**Pros:** Familiar to Unix users, maximally expressive.  
**Cons:** Significant implementation complexity; the rule file pipe-splitting
currently requires exactly 5 fields (`FIELD_COUNT = 5` in `load.py:9`), so a
space-containing sort spec would require changing `_split_ruleline_into_fields`
to split on the first 4 pipes only.

---

## Recommendation

**Option A** is the right first step — it is a two-line change to
`_sort_datalines`, a small `_parse_rule` change, and it solves the immediate
problem. A `3+` sort key sorts by the substring from field 3 to end of line,
which automatically gives field-4 ordering as a tiebreaker.

**Option B** is a clean next step if non-contiguous keys are needed (e.g., sort
by command verb in field 4, then by volume name in field 6).

**Option C** is worth considering only if numeric sort or month sort become
necessary — the complexity cost is real.
