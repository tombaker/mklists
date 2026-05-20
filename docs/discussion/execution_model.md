# Three-level execution model

`mklists` processes data across three nested levels of scope:

1. **Run** — a single invocation; loads config, discovers directories, generates a timestamp
2. **Pass** — one complete sweep over all data directories (default: 1 pass; 2 passes when routing is enabled and there are multiple data directories); owns per-pass invariants such as the backup directory
3. **Datadir** — processes a single directory: safety checks → read files → apply rules (pre-loaded in plan) → delete old files → write new files

## High-level call graph

```
mklists run  (cli.py)
├── resolve_structural_context()   # filesystem discovery
├── resolve_config()               # merge defaults + user YAML
├── resolve_run_plan()             # build execution blueprint
└── run_mklists()
    └── for each pass:
        ├── init_snapshot_dir()    # if backup enabled
        ├── backup_datadirs()      # if backup enabled
        └── for each datadir:
            └── process_datadir()
                ├── run_safety_checks()
                ├── read datafiles          # rules pre-loaded via datadir_plan.rules
                ├── dispatch_datalines_to_targets()
                ├── delete old datafiles
                └── write new datafiles
        └── redistribute_datafiles()  # if routing enabled
    ├── prune_backupdirs()             # if backup enabled
    ├── linkify_md_datadirs()          # if linkify_md_dir configured
    └── linkify_html_datadirs()        # if linkify_html_dir configured
```

## Design principles

* **Runs own passes**
  The loop over passes belongs at the run level. Individual modules (e.g. backups, processing) are not aware of multiple passes.

* **Passes own per-pass invariants**
  Anything invariant across a pass — such as the per-pass backup directory or per-pass log file — is computed once and reused for all data directories in that pass.

* **Datadir processing is isolated**
  `process_datadir()` handles all work inside a single data directory and assumes that any required per-pass setup has already been performed.

* **Backups are mechanical, not policy-driven**
  Backup helpers assume validated paths and copy filesystem state exactly; policy decisions (whether backups are enabled, retention depth, etc.) are handled at higher levels.

This structure keeps responsibilities clear, avoids redundant computation, and makes the execution flow easy to reason about and test.
