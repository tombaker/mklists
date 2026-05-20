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

See [docs/discussion/support_for_audits.md](docs/discussion/support_for_audits.md).
