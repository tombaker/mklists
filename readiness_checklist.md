Readiness Checklist

  Core infrastructure — DONE

  - `exec/run.py` — `run_mklists()` fully implemented
  - `exec/process_datadirs.py` — fully implemented
  - `exec/process_datalines.py` — fully implemented
  - `structure/resolve.py` — fully implemented
  - `config/resolve.py` — fully implemented
  - `plan/resolve.py` — fully implemented
  - `rules/load.py` — fully implemented
  - `exec/backups.py`, `exec/routing.py`, `exec/linkify.py`, `exec/safety.py` — fully implemented

  CLI wiring — NOT DONE

  - `mklists run` — stub only (click.echo("Running mklists run."))
    - Needs to call `resolve_structural_context()` → `resolve_config()` → `resolve_run_plan()` → `run_mklists()`
  - `mklists init datatree` — stub only (`click.echo("Running mklists init datatree.")`)
    - Needs to create `mklists.yaml` and/or `mklists.rules` in the target directory
  - `mklists init datadir` — stub only (`click.echo("Running mklists init datadir.")`)
    - Needs to create `.rules` (and optionally `.mklistsrc`) in the target directory

Missing module

- No `init` module exists anywhere in `src/mklists/` — the logic for creating marker files (`mklists.yaml`, `mklists.rules`, `.rules`, `.mklistsrc`) has not been written yet

---
How init is supposed to work

The marker files defined in `structure/markers.py` are the canonical answer:
- `mklists init datatree`:  `mklists.yaml` (config) and/or `mklists.rules` (shared rules)
- `mklists init datadir`: `.rules` (required); optionally `.mklistsrc` for a self-contained datadir
 
There is no existing init module — it needs to be written from scratch. The tests in tests/cli/test_cli.py currently only verify that the stubs exit cleanly and echo something containing "init"/"run", so they are not a guide to the intended behavior.

---

Bottom line: The tool cannot actually be used yet. `mklists run` does nothing real, and `mklists init` creates no files. The two tasks needed to make it usable are:

  1. Wire `mklists run` in `cli.py` to the existing pipeline
  2. Write and wire `mklists init datatree` / `mklists init datadir` to create the appropriate marker files
