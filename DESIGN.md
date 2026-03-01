# Module design philosophy for `mklists`

Here: design principles used to structure modules in the `mklists` codebase.

## 1. Modules have roles

Each module has only one of the following roles.

### Concept modules

Represent a single domain concept and expose one primary operation.
All other functions are private implementation details.

Examples:
- `config.load_config`
- `rules.load_effective_rules`

### Toolbox modules

Provide a set of independent, reusable operations.

Examples:
- filesystem discovery (`find_datadirs`, `find_datafiles`)
- datafile I/O (`read_datafiles`, `write_datafiles`, `delete_datafiles`)

Toolbox modules:
- expose all functions as public
- do not orchestrate workflows
- do not hide functionality behind private helpers

### Orchestrator modules

Coordinate workflows by calling public functions from other modules.

Examples:
- `process.process_datadir`
- `cli.main`

Orchestrator modules express what happens, not how. 
Complex orchestration logic should be extracted into a new concept or toolbox module rather than hidden behind private functions.

## 2. Public vs private functions

A function is public if:
- it performs a complete, meaningful operation
- it could reasonably be reused elsewhere
- it can be tested in isolation

A function is private if:
- it exists only to support a public function
- it has no standalone semantic meaning

If a function is important enough to name clearly, it is important enough to be public — somewhere.

## 3. Exception handling

Exceptions are caught only to:
- translate low-level errors into domain-specific errors
- enrich errors with additional context

Exceptions are not caught merely to log.
Uncaught exceptions are allowed to terminate execution and are handled by the global logging configuration.

## 4. Modules should read like documentation

A reader should be able to:
- skim the public functions of a module
- understand their purposes immediately
- trust that private functions are implementation details

### Run / Pass / Datadir Execution Model

`mklists` is structured around three nested levels of execution:

1. **Run** – a single invocation of `mklists`
2. **Pass** – one complete sweep over all data directories
3. **Datadir** – processing of a single data directory

This separation exists to make per-pass invariants (such as backups and logging) explicit, and to avoid recomputing them for each data directory.

#### High-level call graph

```
cli.main()
├── parse CLI arguments (e.g. verbosity)
└── run_mklists()
    ├── load configuration
    ├── discover data directories
    ├── generate run-level timestamp
    └── for pass_number in passes (default: 2):
        └── run_pass()
            ├── if backups_enabled:
            │   ├── compute pass_backupdir
            │   ├── initialize pass_backupdir
            │   └── initialize per-pass logging
            ├── for datadir in datadirs:
            │   └── process_datadir()
            │       ├── run safety checks
            │       ├── load effective rules
            │       ├── read datafiles
            │       ├── apply rules
            │       ├── if backups_enabled:
            │       │   └── back up datadir
            │       ├── delete old datafiles
            │       └── write new datafiles
            └── perform routing (if enabled)
```

#### Design principles

* **Runs own passes**
  The loop over passes belongs at the run level. Individual modules (e.g. backups, processing) are not aware of multiple passes.

* **Passes own per-pass invariants**
  Anything invariant across a pass—such as the per-pass backup directory or per-pass log file—is computed once in `run_pass()` and reused for all data directories in that pass.

* **Datadir processing is isolated**
  `process_datadir()` handles all work inside a single data directory and assumes that any required per-pass setup has already been performed.

* **Backups are mechanical, not policy-driven**
  Backup helpers assume validated paths and copy filesystem state exactly; policy decisions (whether backups are enabled, retention depth, etc.) are handled at higher levels.

This structure keeps responsibilities clear, avoids redundant computation, and makes the execution flow of `mklists` easy to reason about and test.
Worth codifying as a convention:
- *_found → filesystem discovery result (may be None)
- *_used → a decision (effective inputs)
- *_to_snapshot → planned side-effect inputs
- *_dir / *_path → derived locations
sets `config_rootdir` as follows:
- If configfile found in startdir, config_rootdir is startdir.
- Or if configfile found in parent of startdir, config_rootdir is parent of startdir.
- Or if no configfile is found, config_rootdir is startdir.

