# Support for audits

`mklists` uses timestamps in three contexts to create an immutable, ordered record of every operation.

## Dispatch filenames

Files moved to a routing destination are named `{timestamp}.{datadir}.{routefile}` — for example, `20260507T053537280790.phone.personz` (12 digits after `T`: `HHMMSS` + 6-digit microseconds). The timestamp prefix guarantees that no dispatch ever overwrites an earlier one, even when the destination directory is on a different volume and is not processed between source runs. Accumulated dispatch files are processed in order when the destination datatree is next run.

## Backup directory names

Each backup run creates a snapshot directory named `{timestamp}_{NN}` inside the configured backup root — for example, `2026-05-07_0535_37280790_01`, where `_01` is the pass number. Directories sort chronologically by name, and no backup ever silently replaces another.

## Log entries

Every log entry carries a timestamp, providing a sequential record of what was read, dispatched, backed up, and transformed in each run.

The common design principle: timestamps provide immutability through uniqueness. No operation silently overwrites an earlier record; every operation leaves a chronologically ordered trace that supports both debugging and reconstruction of past state.
