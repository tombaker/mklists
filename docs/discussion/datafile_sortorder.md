# Datafile sort order

The fifth field of a rule line specifies how the target file is sorted after
matched lines are appended to it.

## Sort key values

| Value | Behaviour |
|---|---|
| _(blank)_ | No sort; lines remain in their current order |
| `0` | Sort on the entire line |
| `N` (integer ≥ 1) | Sort from field N through end of line |

Field numbering is one-based, as in Awk.

## Sort from field N through end of line

A sort key of `N` uses `" ".join(fields[N-1:])` as the sort key — the
whitespace-joined substring from field N to the end of the line. Fields N+1,
N+2, and so on act as natural tiebreakers, giving deterministic ordering even
when field N alone is not unique.

### Example

Given lines sorted by key `3`:

```
::UNIX DISKUTIL diskutil unmount /Volumes/Quoits
::UNIX DISKUTIL diskutil info /Volumes/Platinum | grep "File System"
::UNIX DISKUTIL diskutil apfs addVolume disk3 APFS Conclave -passphrase yourPassphraseHere
```

Field 3 (`diskutil`) is identical for all three lines. With sort key `3`, the
sort key becomes the full remainder of each line from field 3 onward, so
field 4 (`unmount`, `info`, `apfs`) determines the order, and fields 5 and
beyond break any further ties.

## Implementation

`_sort_datalines` in `exec/process_datalines.py`. The sort key is stored on
`Rule.target_sortkey` as `int | None`; it is parsed from the rule file by
`_parse_rule` in `rules/load.py`.
