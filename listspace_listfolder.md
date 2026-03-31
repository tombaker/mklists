# Rename plan: `repo` → `listspace`, `datadir` → `listfolder`

Covers all identifiers, docstrings, comments, CLI subcommands, and documentation.
Does not cover `.venv/` or `.pytest_cache/`.

---

## Term mapping

| Old form | New form | Context |
|---|---|---|
| `REPO` | `LISTSPACE` | screaming snake case |
| `DATADIR` | `LISTFOLDER` | screaming snake case |
| `Repo` | `Listspace` | CamelCase prefix |
| `Datadir` | `Listfolder` | CamelCase prefix |
| `repo` | `listspace` | snake case |
| `datadir` | `listfolder` | snake case |
| `datadirs` | `listfolders` | plural snake case |
| `repository` | `listspace` | prose / docstrings |

One deliberate exception: `snapshot_repofiles_to_copy` → `snapshot_listspace_files`
(not `snapshot_listspacefiles_to_copy`, which would be unreadably long).

---

## 1. Constants (`src/mklists/structure/markers.py`)

| Old | New |
|---|---|
| `REPO_CONFIGFILE_NAME` | `LISTSPACE_CONFIGFILE_NAME` |
| `REPO_RULEFILE_NAME` | `LISTSPACE_RULEFILE_NAME` |
| `DATADIR_CONFIGFILE_NAME` | `LISTFOLDER_CONFIGFILE_NAME` |
| `DATADIR_RULEFILE_NAME` | `LISTFOLDER_RULEFILE_NAME` |

These constants are imported in `structure/__init__.py`, `structure/resolve.py`,
`config/resolve.py`, and several test files — all must be updated in the same step.

---

## 2. Class names

| Old | New | Defined in |
|---|---|---|
| `DatadirStructuralContext` | `ListfolderStructuralContext` | `structure/model.py` |
| `DatadirPlan` | `ListfolderPlan` | `plan/model.py` |
| `SkippedDatadir` | `SkippedListfolder` | `plan/model.py` |

`DatadirStructuralContext` is exported via `structure/__init__.py` and imported in
`structure/resolve.py`, `plan/resolve.py`, and multiple test files.
`DatadirPlan` is exported via `plan/__init__.py` and imported in
`exec/process_datadirs.py` and `exec/run.py`.

---

## 3. Properties and fields on model classes

### `StartdirContext` (inside `StructuralContext`, `structure/model.py`)

| Old | New |
|---|---|
| `repo_configfile_found` | `listspace_configfile_found` |
| `repo_rulefile_found` | `listspace_rulefile_found` |
| `datadir_configfile_found` | `listfolder_configfile_found` |
| `datadir_rulefile_found` | `listfolder_rulefile_found` |
| `is_repo_root` | `is_listspace_root` |
| `is_datadir_selfcontained` | `is_listfolder_selfcontained` |
| `is_datadir_in_repo` | `is_listfolder_in_listspace` |

### `DatadirStructuralContext` → `ListfolderStructuralContext` (`structure/model.py`)

| Old | New |
|---|---|
| `datadir` | `listfolder` |
| `datadir_configfile_found` | `listfolder_configfile_found` |
| `datadir_rulefile` | `listfolder_rulefile` |

### `StructuralContext` (`structure/model.py`)

| Old | New |
|---|---|
| `datadir_contexts` | `listfolder_contexts` |

### `DatadirPlan` → `ListfolderPlan` (`plan/model.py`)

| Old | New |
|---|---|
| `datadir` | `listfolder` |

### `SkippedDatadir` → `SkippedListfolder` (`plan/model.py`)

| Old | New |
|---|---|
| `datadir` | `listfolder` |
| `datadir_configfile_found` | `listfolder_configfile_found` |

### `PassPlan` (`plan/model.py`)

| Old | New |
|---|---|
| `datadir_plans` | `listfolder_plans` |
| `skipped_datadirs` | `skipped_listfolders` |
| `snapshot_repofiles_to_copy` | `snapshot_listspace_files` |

---

## 4. Function names

| Old | New | Defined in |
|---|---|---|
| `_find_datadirs` | `_find_listfolders` | `structure/resolve.py` |
| `_resolve_datadir_context` | `_resolve_listfolder_context` | `structure/resolve.py` |
| `_resolve_datadir_plans` | `_resolve_listfolder_plans` | `plan/resolve.py` |
| `load_rules_for_datadir` | `load_rules_for_listfolder` | `rules/load.py` |
| `backup_datadirs` | `backup_listfolders` | `exec/backups.py` |
| `process_datadir` | `process_listfolder` | `exec/process_datadirs.py` (see §6) |
| `linkify_datadirs` | `linkify_listfolders` | `exec/linkify.py` |

`load_rules_for_datadir` is exported via `rules/__init__.py` and imported in
`plan/resolve.py`.
`backup_datadirs` and `process_datadir` are exported via `exec/__init__.py`.
`linkify_datadirs` is exported via `exec/__init__.py` and called in `exec/run.py`.

---

## 5. Local variables and parameters

Affects every function that iterates over or receives a single directory or a list
of directories. Apply throughout `structure/resolve.py`, `plan/resolve.py`,
`exec/run.py`, `exec/backups.py`, `exec/linkify.py`, `exec/routing.py`,
`exec/process_datadirs.py`, and `exec/safety.py`.

| Old | New |
|---|---|
| `datadir` (parameter or loop variable) | `listfolder` |
| `datadirs` (parameter or local list) | `listfolders` |
| `datadir_ctx` | `listfolder_ctx` |
| `datadir_context` | `listfolder_context` |
| `datadir_contexts` | `listfolder_contexts` |
| `datadir_plan` | `listfolder_plan` |
| `is_datadir` (local bool) | `is_listfolder` |
| `is_repo_root` (local bool, distinct from the property) | `is_listspace_root` |
| `repo_rulefile` (local) | `listspace_rulefile` |
| `repo_configfile` (local) | `listspace_configfile` |
| `repo_cfg` (local) | `listspace_cfg` |
| `repo_rules` (local) | `listspace_rules` |
| `repofile_to_snapshot` (loop variable) | `listspace_file_to_snapshot` |
| `snapshot_repofiles_to_copy` (local) | `snapshot_listspace_files` |

In test files, local variables named `repo`, `repo_marker`, `repo_cfg`,
`repo_rules`, `repo_configfile`, `repo_rulefile` follow the same mapping.

---

## 6. File renames

### Source files

| Old path | New path |
|---|---|
| `src/mklists/exec/process_datadirs.py` | `src/mklists/exec/process_listfolders.py` |

Update imports in:
- `src/mklists/exec/__init__.py`
- `src/mklists/exec/run.py`

### Test files

| Old path | New path |
|---|---|
| `tests/plan/test__resolve_datadir_plans.py` | `tests/plan/test__resolve_listfolder_plans.py` |
| `tests/rules/test_load_rules_for_datadir.py` | `tests/rules/test_load_rules_for_listfolder.py` |
| `tests/exec/backups/test_backup_datadirs.py` | `tests/exec/backups/test_backup_listfolders.py` |
| `tests/exec/linkify/test_linkify_datadirs.py` | `tests/exec/linkify/test_linkify_listfolders.py` |

No source files import test files, so no import updates are needed for test renames.
Use `git mv` to preserve history.

---

## 7. CLI subcommands (`src/mklists/cli.py`)

| Old | New |
|---|---|
| `mklists init repo` (subcommand name and function `repo`) | `mklists init listspace` (function `listspace`) |
| `mklists init datadir` (subcommand name and function `datadir`) | `mklists init listfolder` (function `listfolder`) |

The function name is also the Click subcommand name, so renaming the function
changes the CLI surface directly.

---

## 8. Documentation files

### `DESIGN.md`

- Section heading "Run / Pass / Datadir Execution Model" → "Run / Pass / Listfolder Execution Model"
- All occurrences of `datadir` in prose, examples, and the call graph
  (`process_datadir`, `find_datadirs`, `back up datadir`, `for datadir in datadirs`)
- `Datadir processing is isolated` design principle heading and body

### `CLAUDE.md`

- Architecture section: "datadirs" → "listfolders" throughout
- Call graph: `backup_datadirs`, `process_datadir`, `linkify_datadirs`,
  `for each datadir`, `for each pass`
- Module roles table: `process_datadir` entry
- Key source locations table: `exec/process_datadirs.py` → `exec/process_listfolders.py`

### `README.md`

Currently empty; no changes required.

---

## 9. Docstrings and inline comments

Every docstring or comment that uses "repo", "repository", or "datadir" as a
prose noun needs updating. The highest-density files are:

- `structure/markers.py` — module docstring defines both terms
- `structure/model.py` — docstrings on every property
- `structure/resolve.py` — function and parameter docstrings
- `plan/model.py` — class and field docstrings
- `plan/resolve.py` — function docstrings
- `exec/backups.py` — parameter docstrings
- `exec/linkify.py` — module and function docstrings
- `exec/process_datadirs.py` — module and function docstrings
- `config/resolve.py` — parameter docstrings (`config_rootdir: Root directory of mklists repo.`)
- `errors.py` — class docstring (`Invalid repository or datadir structure.`)

---

## 10. Execution order

Perform changes in this order to keep the codebase in a buildable state at each step:

1. **Constants** (`markers.py`) and their imports (`structure/__init__.py`) — everything downstream depends on these names.
2. **Model classes and their fields** (`structure/model.py`, `plan/model.py`) — class names and field names together, since they are defined and referenced in the same files.
3. **`structure/__init__.py`** — update re-exports to match new class names.
4. **`plan/__init__.py`** and **`rules/__init__.py`** and **`exec/__init__.py`** — update re-exports.
5. **Concept and toolbox modules** (`structure/resolve.py`, `plan/resolve.py`, `rules/load.py`, `config/resolve.py`, `exec/backups.py`, `exec/linkify.py`, `exec/routing.py`, `exec/safety.py`) — update function names, parameters, and local variables.
6. **File rename**: `process_datadirs.py` → `process_listfolders.py`; update its imports in `exec/__init__.py` and `exec/run.py` in the same commit.
7. **Orchestrators** (`exec/run.py`, `cli.py`) — update function calls and CLI subcommand names.
8. **Test files** — update all identifier references, then rename the four test files with `git mv`.
9. **Documentation** (`DESIGN.md`, `CLAUDE.md`) — update prose, headings, and call graphs.

---

## 11. Verification

After all changes:

```bash
cd /Users/tbaker/github/tombaker/mklists && poetry run python -m pytest
cd /Users/tbaker/github/tombaker/mklists && poetry run mypy src/
cd /Users/tbaker/github/tombaker/mklists && poetry run ruff check src/
```

Confirm no residual occurrences of the old terms in source or tests:

```bash
grep -r "datadir\|repo_\|REPO_\|DATADIR_\|is_repo\|is_datadir" src/ tests/
```

The only expected survivors after the rename are:
- Occurrences of `repo` as a path component in test fixtures
  (e.g., `tmp_path / "repo" / "a"` used as arbitrary directory names) —
  these are test scaffold paths, not terminology, and may be left or renamed
  to `tmp_path / "listspace" / "a"` for consistency.
- Any occurrence of `datadir` inside string literals that represent actual
  filesystem paths or user-visible output (search separately with `-F` for
  exact strings).
