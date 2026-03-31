# Rename plan: `repo` → `dataspace`, `datadir` unchanged

Covers all identifiers, docstrings, comments, CLI subcommands, and documentation.
Does not cover `.venv/` or `.pytest_cache/`.

The term `datadir` is kept exactly as it is throughout.
The term `repo` (and `repository` in prose) is replaced by `dataspace`.
Where a variable or function currently carries `repo_` to signal "belongs to the
dataspace root", that `repo_` prefix becomes `dataspace_` — so the notion of a
root directory is preserved via `dataspace_rootdir` and friends.

---

## Term mapping

| Old form | New form | Context |
|---|---|---|
| `REPO` | `DATASPACE` | screaming snake case |
| `Repo` | `Dataspace` | CamelCase prefix |
| `repo` | `dataspace` | snake case |
| `repository` | `dataspace` | prose / docstrings |

`datadir`, `datadirs`, `DATADIR`, `Datadir` are **not changed**.

One deliberate exception: `snapshot_repofiles_to_copy` → `snapshot_dataspace_files`
(not `snapshot_dataspacefiles_to_copy`, which would be unreadably long).

---

## 1. Constants (`src/mklists/structure/markers.py`)

| Old | New |
|---|---|
| `REPO_CONFIGFILE_NAME` | `DATASPACE_CONFIGFILE_NAME` |
| `REPO_RULEFILE_NAME` | `DATASPACE_RULEFILE_NAME` |

`DATADIR_CONFIGFILE_NAME` and `DATADIR_RULEFILE_NAME` are unchanged.

These constants are imported in `structure/__init__.py`, `structure/resolve.py`,
`config/resolve.py`, and several test files — all must be updated in the same step.

The module docstring currently reads:

> A Repo Root is marked by the presence of `mklists.yaml` and/or `mklists.rules`.

This becomes:

> A Dataspace root is marked by the presence of `mklists.yaml` and/or `mklists.rules`.

---

## 2. Class names

No class is named `Repo*` today, so no class renames are required.
`DatadirStructuralContext`, `DatadirPlan`, and `SkippedDatadir` are all unchanged.

---

## 3. Properties and fields on model classes

### `StartdirStructuralContext` (`structure/model.py`)

| Old | New |
|---|---|
| `repo_configfile_found` | `dataspace_configfile_found` |
| `repo_rulefile_found` | `dataspace_rulefile_found` |
| `is_repo_root` | `is_dataspace_root` |

`datadir_configfile_found`, `datadir_rulefile_found`, `is_datadir_selfcontained`,
and `is_datadir_in_repo` are unchanged.

The property docstring changes from:

> True if startdir is the root directory of a repository of datadirs.

to:

> True if startdir is the root directory of a dataspace.

`is_datadir_in_repo` gains a small prose update:

> True if startdir is a datadir within a dataspace.

### `PassPlan` (`plan/model.py`)

| Old | New |
|---|---|
| `snapshot_repofiles_to_copy` | `snapshot_dataspace_files` |

---

## 4. Function names

No public function is named `repo*`, so no function renames are required.
All `datadir`-named functions (`backup_datadirs`, `process_datadir`,
`linkify_datadirs`, `load_rules_for_datadir`, `_find_datadirs`,
`_resolve_datadir_context`, `_resolve_datadir_plans`) are unchanged.

---

## 5. Local variables and parameters

Affects every function that reads or passes `repo_*` locals.

### `structure/resolve.py`

| Old | New |
|---|---|
| `repo_configfile_found` (local) | `dataspace_configfile_found` |
| `repo_rulefile_found` (local) | `dataspace_rulefile_found` |
| `is_repo_root` (local bool) | `is_dataspace_root` |

The error-message strings change accordingly:

> "Starting directory cannot be both repository root and datadir."
> → "Starting directory cannot be both dataspace root and datadir."

> "Starting directory must be repository root or datadir."
> → "Starting directory must be dataspace root or datadir."

Also update `repo_configfile_found=` and `repo_rulefile_found=` keyword arguments
in the `StartdirStructuralContext(...)` constructor call to match the renamed fields.

Call sites that use `startdir_context.is_repo_root` must be updated to
`startdir_context.is_dataspace_root` in `structure/resolve.py`, `config/resolve.py`,
and `exec/run.py` (if applicable).

### `plan/resolve.py`

| Old | New |
|---|---|
| `repo_rulefile` (local) | `dataspace_rulefile` |
| `snapshot_repofiles_to_copy` (local) | `snapshot_dataspace_files` |
| `snapshot_repofiles_to_copy=` (keyword arg to `PassPlan(...)`) | `snapshot_dataspace_files=` |
| `startdir_context.repo_rulefile_found` (access) | `startdir_context.dataspace_rulefile_found` |
| `startdir_context.repo_configfile_found` (access) | `startdir_context.dataspace_configfile_found` |

### `config/resolve.py`

| Old | New |
|---|---|
| `repo_configfile` (local) | `dataspace_configfile` |
| `startdir_context.repo_configfile_found` (access) | `startdir_context.dataspace_configfile_found` |
| `startdir_context.is_repo_root` (access) | `startdir_context.is_dataspace_root` |

Parameter docstrings that read `Root directory of mklists repo.` become
`Root directory of mklists dataspace.`

### `exec/backups.py`

| Old | New |
|---|---|
| `snapshot_repofiles_to_copy` (parameter) | `snapshot_dataspace_files` |
| `repofile_to_snapshot` (loop variable) | `dataspace_file_to_snapshot` |

Docstring: `List of repo-level config files to back up.`
→ `List of dataspace-level config files to back up.`

### `exec/run.py`

| Old | New |
|---|---|
| `pass_plan.snapshot_repofiles_to_copy` (access) | `pass_plan.snapshot_dataspace_files` |
| keyword arg `snapshot_repofiles_to_copy=` (call to `init_snapshot_dir`) | `snapshot_dataspace_files=` |

### Test files

In every test file that references `repo_configfile_found`, `repo_rulefile_found`,
`is_repo_root`, `snapshot_repofiles_to_copy`, `REPO_CONFIGFILE_NAME`, or
`REPO_RULEFILE_NAME`, apply the corresponding mapping above.

Local variables in tests named `repo`, `repo_marker`, `repo_cfg`, `repo_rules`,
`repo_configfile`, `repo_rulefile` follow the same `repo_` → `dataspace_` mapping.

---

## 6. File renames

No source or test files need to be renamed (no file is named `repo*`).

---

## 7. CLI subcommands (`src/mklists/cli.py`)

| Old | New |
|---|---|
| `mklists init repo` (subcommand name and function `repo`) | `mklists init dataspace` (function `dataspace`) |

The `init` group docstring changes from:

> Initialize a new mklists repo or datadir (data directory).

to:

> Initialize a new mklists dataspace or datadir (data directory).

The `repo` function docstring changes from:

> Initialize a new mklists repo (where datadirs share rules).

to:

> Initialize a new mklists dataspace (where datadirs share rules).

---

## 8. Documentation files

### `DESIGN.md`

- All occurrences of `repo`, `Repo Root`, and `repository` in prose, headings,
  and the call graph; replace with `dataspace`, `Dataspace root`, and `dataspace`.

### `CLAUDE.md`

- Architecture section: `repo` → `dataspace` in prose and the call graph.
- CLAUDE.md also mentions `config_rootdir` — that name is **not** changed; it is a
  derived filesystem path, not a naming of the concept, and `rootdir` suffix already
  conveys its meaning clearly.

### `README.md`

Currently empty; no changes required.

---

## 9. Docstrings and inline comments

Every docstring or comment that uses `repo`, `Repo Root`, or `repository` as a
prose noun needs updating. The highest-density files are:

- `structure/markers.py` — module docstring defines the term
- `structure/model.py` — property docstrings on `is_repo_root`, `is_datadir_in_repo`
- `structure/resolve.py` — inline comments and error-message strings
- `plan/model.py` — field docstring for `snapshot_repofiles_to_copy`
- `plan/resolve.py` — inline comments referencing `repo_rulefile`
- `exec/backups.py` — parameter docstring
- `config/resolve.py` — parameter docstrings (`config_rootdir: Root directory of mklists repo.`)
- `errors.py` — class docstring (`Invalid repository or datadir structure.`)

---

## 10. Names that do NOT change

The following names carry `root` or `rootdir` and describe filesystem paths rather
than the concept being renamed; they are correct as they stand:

| Name | Location | Reason unchanged |
|---|---|---|
| `config_rootdir` | `StartdirStructuralContext`, `config/resolve.py` | Describes a derived path, not the dataspace concept |
| `backup_rootdir` | `BackupPlan` (`plan/model.py`) | Describes the backup root path |

---

## 11. Execution order

Perform changes in this order to keep the codebase in a buildable state at each step:

1. **Constants** (`markers.py`) and their imports (`structure/__init__.py`) —
   rename `REPO_CONFIGFILE_NAME` → `DATASPACE_CONFIGFILE_NAME` and
   `REPO_RULEFILE_NAME` → `DATASPACE_RULEFILE_NAME`; everything downstream depends
   on these names.
2. **Model fields** (`structure/model.py`) — rename `repo_configfile_found`,
   `repo_rulefile_found`, `is_repo_root` together, since the property body
   references the fields.
3. **`structure/__init__.py`** — update re-exports if any `repo_*` names are
   re-exported.
4. **`plan/model.py`** — rename `snapshot_repofiles_to_copy`.
5. **Concept and toolbox modules** (`structure/resolve.py`, `config/resolve.py`,
   `plan/resolve.py`, `exec/backups.py`) — update local variables, parameters,
   field accesses, and docstrings.
6. **Orchestrators** (`exec/run.py`, `cli.py`) — update field accesses and
   CLI subcommand name.
7. **Test files** — update all identifier references.
8. **Documentation** (`DESIGN.md`, `CLAUDE.md`) — update prose and call graphs.

---

## 12. Verification

After all changes:

```bash
cd /Users/tbaker/github/tombaker/mklists && poetry run mypy src/
cd /Users/tbaker/github/tombaker/mklists && poetry run ruff check src/
```

Confirm no residual occurrences of the old terms in source or tests:

```bash
grep -r "repo_\|REPO_\|is_repo\|repository\b" src/ tests/
```

The only expected survivors are:

- Occurrences of `repo` as an arbitrary path component in test fixtures
  (e.g., `tmp_path / "repo" / "a"` used as an unrelated directory name) —
  these may be left as-is or renamed to `tmp_path / "dataspace" / "a"` for
  consistency.
- Any occurrence of `repo` inside string literals that represent actual filesystem
  paths or user-visible CLI output (search separately with `grep -F repo`).
