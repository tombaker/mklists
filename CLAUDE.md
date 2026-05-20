# CLAUDE.md

Guides Claude Code (claude.ai/code) when working on code for `mklists`.

## Coding style

- Prefer explicit `if/else` blocks to ternary (conditional) expressions.
- Use [Click](https://click.palletsprojects.com/) for the CLI (`cli.py`).

## Communication style

- Never use informal contractions (e.g., "it's", "that's", "don't", "isn't");
  always use the full form (e.g., "it is", "that is", "do not", "is not")

## Installation

To make `mklists` available globally — in every shell session, regardless of
which Poetry venv (if any) is active — install it with
[pipx](https://pipx.pypa.io/):

```bash
pipx install --editable /Users/tbaker/github/tombaker/mklists
```

`pipx` creates an isolated virtual environment for the tool and symlinks the
`mklists` entry point into `~/.local/bin` (which is on `PATH`). The
`--editable` flag installs from the local source tree, so edits to the source
take effect immediately without reinstalling.

## Git hooks

The `hooks/` directory is version-controlled and contains a `pre-commit` hook
that runs pytest, ctags, and pylint before every commit. Git must be told to
use it — this setting is stored in `.git/config` and is not tracked, so it must
be set once per clone:

```bash
git config core.hooksPath hooks
```

## Related projects

`/Users/tbaker/n4ma/nalter` is a sibling Python project by the same author.
Consult it as a reference for shared tooling decisions: MkDocs setup,
pre-commit hooks, pylint configuration, Poetry workflow, and coding style.

To make changes in `nalter` based on code or settings here, the user must run
`claude` from within `/Users/tbaker/n4ma/nalter/`. Claude Code's working
directory determines which project is active: which `CLAUDE.md` is loaded,
which memory files are used, and where edits land. The cross-reference above
means Claude will know to look at this project for reference without being told
the path, but the actual work happens in whichever project `claude` was started
from.

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

See [docs/discussion/execution_model.md](docs/discussion/execution_model.md).

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

### Linkify

See [docs/configuration/linkify.md](docs/configuration/linkify.md). Public functions: `linkify_md_datadirs()` and `linkify_html_datadirs()`; both delegate to the private `_mirror_datadirs(datadirs, output_dir, suffix)` helper.

### Binary file detection heuristic

See [docs/configuration/binary_file_detection.md](docs/configuration/binary_file_detection.md). Implemented in `_check_file_contents` in `exec/safety.py`.
