# Sort order options for mklists

## Current state (before this change)

The rule file's 5th field is a single integer parsed in `load.py:151`
(`int(raw_sortorder)`). The sort in `process_datalines.py:131` extracts one
whitespace-delimited field and sorts on that string alone. Fields beyond the
sort key are ignored, so ties are broken arbitrarily by Python's stable sort
(i.e., original list order).

## Decision

A sort key of N now means "sort from field N through the end of the line."
The sort key in `_sort_datalines` (`process_datalines.py`) becomes
`" ".join(fields[N-1:])` instead of `fields[N-1]`.

This requires no change to `Rule`, `load.py`, or the rule file format. A rule
specifying sort key `3` now sorts by the substring from field 3 to end of line,
which automatically gives field 4, field 5, etc. as tiebreakers.

### Example

Given lines sorted by key `3`:

```
::UNIX DISKUTIL diskutil unmount /Volumes/Quoits
::UNIX DISKUTIL diskutil info /Volumes/Platinum | grep "File System"
::UNIX DISKUTIL diskutil apfs addVolume disk3 APFS Conclave -passphrase yourPassphraseHere
```

Previously, field 3 (`diskutil`) is the same for all lines, so field 4 order
was arbitrary. With "field 3 to end", the sort key becomes the full remainder
of the line from field 3 onward, giving deterministic ordering based on field 4
and beyond.

## Options considered but not taken

### Option B — Comma-separated field list (`3,4` or `3,4,5`)

The sort key becomes a tuple `(field3_text, field4_text, ...)`, which Python
compares lexicographically. Handles non-contiguous keys (e.g., sort by field 5
then field 2). Rejected as unnecessary complexity given that "field N to end"
covers the common case.

### Option C — Full `sort(1)`-style spec

Parse a mini-language like `3,4 4n,5` supporting numeric (`n`), reverse (`r`),
and month (`M`) sort modifiers. Maximum expressiveness, but significant
implementation complexity. The rule file pipe-splitting would also need to
change since field 5 currently cannot contain spaces. Rejected for now.
