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

See [docs/discussion/execution_model.md](docs/discussion/execution_model.md).

## 5. Support for audits

`mklists` uses timestamps in three contexts to create an immutable, ordered record of every operation.

### Dispatch filenames

Files moved to a routing destination are named `{timestamp}.{datadir}.{routefile}` — for example, `20260507T053537280790.phone.personz` (12 digits after `T`: `HHMMSS` + 6-digit microseconds). The timestamp prefix guarantees that no dispatch ever overwrites an earlier one, even when the destination directory is on a different volume and is not processed between source runs. Accumulated dispatch files are processed in order when the destination datatree is next run.

### Backup directory names

Each backup run creates a snapshot directory named `{timestamp}_{NN}` inside the configured backup root — for example, `2026-05-07_0535_37280790_01`, where `_01` is the pass number. Directories sort chronologically by name, and no backup ever silently replaces another.

### Log entries

Every log entry carries a timestamp, providing a sequential record of what was read, dispatched, backed up, and transformed in each run.

The common design principle: timestamps provide immutability through uniqueness. No operation silently overwrites an earlier record; every operation leaves a chronologically ordered trace that supports both debugging and reconstruction of past state.
