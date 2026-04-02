# Nested datadirs in mklists

## What the current model assumes (and would break)

The entire pipeline rests on one structural invariant: **a datadir is exactly one level below the datatree root.** This assumption is encoded in at least four places:

1. **`_find_datadirs`** (`structure/resolve.py:60`) — uses `config_rootdir.iterdir()`, a shallow scan. It would simply never see `computing/abc`.

2. **`config_rootdir` resolution** (`structure/model.py:43`) — when starting from a datadir-in-datatree, it resolves `config_rootdir` as `startdir.parent`. For `computing/abc`, that yields `computing/`, not the datatree root, so `mklists.yaml` and the backup directory would not be found.

3. **`_resolve_datadir_plans`** (`plan/resolve.py:88`) — the rule chain is `[datatree_rulefile, datadir_rulefile]`. There is no slot for an intermediate `computing/.rules`.

4. **Routing targets** (`routing_dict`) — currently maps bare filenames to bare datadir names (e.g., `"todo.txt" → "inbox"`). With nesting, target names would need to be paths (`"todo.txt" → "projects/ana"`), changing config syntax.

---

## The two sub-cases

The design raises two distinct questions:

**Sub-case A — pure container directories** (`computing/` has no `.rules`)
The intermediate directories are transparent organizational wrappers. Mklists would discover datadirs at arbitrary depth, but each datadir still behaves exactly as now: isolated processing, no cross-level rule inheritance.

**Sub-case B — intermediate datadirs** (`computing/` also has `.rules`)
The intermediate directory is itself a datadir that can contain data files. Now a line could live in `computing/` and be dispatched into `computing/abc/`. This raises deeper questions: do nested datadirs process parent-before-child? Can a rule route a line from a child up into a parent?

Sub-case A is much cleaner. Sub-case B would require rethinking the processing order and isolation model.

---

## Minimum changes for sub-case A

| Layer | Change needed |
|---|---|
| `_find_datadirs` | Replace `iterdir()` with a recursive walk (`rglob("**/.rules")` or explicit DFS), collecting containing directories. |
| `config_rootdir` resolution | Walk up from startdir until `mklists.yaml` is found, rather than assuming `startdir.parent` is the root. |
| Routing config | Routing targets become relative paths from `config_rootdir` (e.g., `computing/abc`). |
| Backup | Snapshot paths must preserve the relative hierarchy below `config_rootdir`, not flatten to bare directory names. |
| `StructuralContext` / `StartdirStructuralContext` | The "neither root nor datadir" case (an intermediate container) must not raise `StructureError` — or running from such a directory must be explicitly disallowed with a clear message. |

---

## Complications worth weighing

**Accidental discovery.** The recursive walk would pick up any `.rules` file anywhere under the root — including inside a backup directory or a `.git` subtree. The current flat model cannot accidentally discover those because it only looks one level deep. You would need an explicit exclude list or a convention (e.g., directories starting with `.` or `_` are never datadirs).

**Rule inheritance ambiguity.** Even in sub-case A, it is natural to want `computing/.rules` to apply to all computing datadirs (a group-level rule). But if `computing/` has no `.rules`, the rule chain is still just `[datatree_rules, datadir_rules]` — the hierarchy is only organizational, not functional. That may be fine, but it means the nesting buys only filesystem organization, not rule scoping.

**Routing naming.** Currently a routing target is a bare name that identifies a sibling datadir unambiguously. With nesting, names can collide (`computing/abc` vs. `projects/abc`). Relative paths fix this but make routing config more verbose and fragile.

**Conceptual weight vs. actual gain.** In the motivating example, the nesting serves purely organizational purposes — grouping datadirs by topic. The same goal is achievable today with a naming convention: `computing-abc`, `computing-abcd`, `computing-apy`, `projects-adcmi`, `projects-ana`. That costs nothing architecturally. The question is whether the filesystem hierarchy is worth the structural complexity.

---

## Summary judgment

Sub-case A (pure containers, no intermediate datadirs) is architecturally feasible. The core processing pipeline (`process_datadir`, `dispatch_datalines_to_targets`, safety checks) is untouched — it operates on one datadir at a time and does not care about depth. The changes are concentrated in discovery (`_find_datadirs`), `config_rootdir` resolution, routing naming, and backup path structure.

Sub-case B introduces ordering dependencies and potentially breaks the isolation invariant, and is not recommended.

The main risk of sub-case A is the accidental-discovery problem: a shallow scan is naturally bounded; a recursive scan requires explicit exclusion logic to stay well-behaved. That is the first thing to design carefully before any implementation.
