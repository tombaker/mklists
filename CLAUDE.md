# CLAUDE.md

Guides Claude Code (claude.ai/code) when working on code for `mklists`.

## Coding style

- Prefer explicit `if/else` blocks to ternary (conditional) expressions.
- Use [Click](https://click.palletsprojects.com/) for the CLI (`cli.py`).

## Communication style

- Never use informal contractions (e.g., "it's", "that's", "don't", "isn't"); always use the full form (e.g., "it is", "that is", "do not", "is not")

## Commands

Do NOT run `pytest` or any test commands. The user runs tests independently.

Other commands must be prefixed with `cd /Users/tbaker/github/tombaker/mklists &&`, for example:

```bash
cd /Users/tbaker/github/tombaker/mklists && poetry run black src/ tests/
cd /Users/tbaker/github/tombaker/mklists && poetry run ruff check src/
cd /Users/tbaker/github/tombaker/mklists && poetry run mypy src/
```

Note: `pytest.ini` enables `--doctest-modules`, so doctests in source modules are collected automatically.

## Architecture

`mklists` is a rule-based file transformation tool. It reads lines from files in "data directories," applies regex-based dispatch rules, and rewrites sorted output files.

### Three-level execution model

1. **Run** — a single invocation; loads config, discovers directories, generates a timestamp
2. **Pass** — one complete sweep over all data directories (default: 1 pass; 2 passes when routing is enabled and there are multiple data directories); owns per-pass invariants like the backup directory
3. **Datadir** — processes a single directory: safety checks → read files → apply rules (pre-loaded in plan) → delete old files → write new files

High-level call graph:
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
                └── write new datafiles
        └── redistribute_datafiles()  # if routing enabled
    ├── prune_backupdirs()         # if backup enabled
    └── linkify_datadirs()         # if linkify enabled
```

### Module roles (from DESIGN.md)

- **Concept modules** — represent one domain concept, expose one primary public operation (e.g., `config/resolve.py`, `rules/load.py`)
- **Toolbox modules** — reusable independent operations, all public (e.g., filesystem I/O helpers)
- **Orchestrator modules** — coordinate workflows by calling public functions from other modules; express *what* happens, not *how* (e.g., `exec/run.py`, `cli.py`)

Exception handling rule: catch only to translate low-level errors into domain errors or add context — never just to log.

### Context objects

Three context dataclasses thread state through the pipeline:

- **`StructuralContext`** (`structure/model.py`) — result of filesystem discovery: data directories, config file location, rule files, `config_rootdir`
  - `config_rootdir` is the startdir if the config file is there, its parent if the config is there, or startdir by default; it is used to resolve relative backup and urlify directories
- **`Config`** (`config/model.py`) — normalized configuration merged from defaults and user YAML; contains `BackupConfig`, `RoutingConfig`, `SafetyConfig`, `LinkifyConfig`
- **`RunPlan`** (`plan/model.py`) — execution blueprint: list of `PassPlan` objects, each containing `DatadirPlan` objects with resolved rules

### Naming conventions

| Suffix | Meaning |
|---|---|
| `*_found` | filesystem discovery result (may be `None`) |
| `*_used` | effective decision/input |
| `*_to_snapshot` | planned side-effect input |
| `*_dir` / `*_path` | derived filesystem location |

### Key source locations

| Path | Purpose |
|---|---|
| `src/mklists/cli.py` | CLI entry point |
| `src/mklists/exec/run.py` | Main run orchestrator |
| `src/mklists/exec/process_datadirs.py` | Single-datadir processor |
| `src/mklists/exec/process_datalines.py` | Rule dispatch logic |
| `src/mklists/structure/resolve.py` | Filesystem discovery |
| `src/mklists/config/resolve.py` | Config merging |
| `src/mklists/rules/load.py` | Rule file parsing |
| `src/mklists/plan/resolve.py` | Run plan construction |
| `src/mklists/errors.py` | Exception hierarchy |

Tests mirror source structure under `tests/`.

### Binary file detection heuristic

`_check_file_contents` in `exec/safety.py` reads the first 8192 bytes of each file and raises an error if a NUL byte (`\x00`) is found. This is the same heuristic used by ripgrep: both treat NUL-byte presence in the leading 8192-byte window as the signal for binary content. The practical difference is purpose — ripgrep uses the result to suppress output, while mklists uses it to abort processing.
