# Design notes: logging in mklists

## Current state

`src/mklists/logging.py` exists and uses `loguru`. It defines `init_logger(logfile, verbose)`
which configures a stdout sink (when `verbose=True`) and an optional file sink.
`verbose` is already present in `Config` and `DEFAULT_CONFIG_YAML` (default: `False`).

**The critical gap**: `init_logger` is never called anywhere — not in `cli.py`, not in
`run.py`. Logging infrastructure exists but is entirely unwired. No module issues
`logger.info()` calls either. The logging module is effectively dead code.

---

## The question: keep loguru or migrate to stdlib `logging`?

### Case for keeping loguru

- Already in `pyproject.toml` as a dependency; removing it is a small cost.
- Simpler API for basic use: `from loguru import logger` then `logger.info(...)`.
- Better default formatting out of the box.
- `init_logger` is already written.

### Case for migrating to stdlib `logging`

1. **One fewer dependency.** Loguru is a runtime dependency with no other justification
   than convenience. Stdlib logging covers every requirement mklists has.

2. **pytest `caplog` works natively.** Testing loguru output requires either a loguru
   sink fixture or a third-party bridge (`loguru-caplog`). Stdlib logging integrates
   with pytest's `caplog` fixture directly — no extra machinery.

3. **Named loggers are the correct pattern for a tool/library.**
   `logging.getLogger("mklists")` gives users and embedders fine-grained control
   (e.g. `logging.getLogger("mklists").setLevel(logging.WARNING)`). Loguru's global
   singleton is hostile to this.

4. **Precedent in this codebase's ecosystem.** The `nalter` project (a related project
   by the same author) completed exactly this migration. Its conftest shows the
   resulting pattern: named logger `logging.getLogger("nalter")`, handler fixtures
   that yield and clean up, and `caplog`-based tests. The pattern is proven.

5. **`init_logger` is unwired anyway.** Since no code actually calls it yet, the
   migration cost is low — we are not replacing working call sites, only replacing
   the module itself before wiring it up.

**Recommendation: migrate to stdlib `logging`.**

---

## Proposed design

### Logger name

```python
import logging
logger = logging.getLogger("mklists")
```

One named logger for the whole package. Modules that need to log import it:

```python
from mklists.logging import logger
```

### Configuration (wiring)

`init_logger` becomes a thin setup function called once from `cli.py`, after
`resolve_config` returns:

```python
def init_logger(*, verbose: bool, logfile: Path | None = None) -> None:
    """Configure the mklists logger for a run."""
    logger = logging.getLogger("mklists")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    if verbose:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

    if logfile is not None:
        handler = logging.FileHandler(logfile)
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        )
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)
```

### What gets logged

| Event | Level | Location | Message |
|---|---|---|---|
| Start of run | INFO | `run.py` | `"mklists run started"` |
| Each datadir processed | INFO | `run.py` | Full path of datadir |
| Each pass | DEBUG | `run.py` | Pass number |
| Skipped datadir | INFO | `run.py` | Path + reason (self-contained) |
| End of run | INFO | `run.py` | `"mklists run complete"` |

The datadir path message is the user's original request and is the primary motivation
for wiring up logging. With `verbose: False` (the default), nothing is printed.
With `verbose: True` (in config or via a future `--verbose` CLI flag), each datadir
path appears on stdout as it is processed.

### `verbose` in config vs. a `--verbose` CLI flag

Currently `verbose` is in `Config` (and thus in `mklists.yaml` / `.mklistsrc`).
A `--verbose` CLI flag could override this at runtime without editing the config file.
Click makes this straightforward: pass `verbose` from config into `init_logger`,
but allow a `--verbose` flag on `mklists run` to override it.

This is worth implementing but is a separate task from the logging migration itself.

### Testing

With stdlib logging, tests use pytest's `caplog` fixture directly:

```python
def test_run_logs_datadir(tmp_path, caplog):
    ...
    with caplog.at_level(logging.INFO, logger="mklists"):
        run_mklists(run_plan)
    assert str(datadir) in caplog.text
```

No third-party bridges, no loguru sink fixtures.

The nalter `conftest.py` shows an alternative pattern using handler fixtures
(`tmplogger_to_stderr`, `tmplogger_with_pathname`) for tests that need to inspect
a log file on disk. Mklists can adopt the same pattern when logfile tests are needed.

---

## Migration steps (when ready to implement)

1. Remove `loguru` from `pyproject.toml` dependencies.
2. Rewrite `src/mklists/logging.py` using stdlib `logging` as above.
3. Call `init_logger` from `cli.py` after `resolve_config`.
4. Add `logger.info(datadir_plan.datadir)` in the per-datadir loop in `run.py`.
5. Add `caplog`-based tests for the logged output.
6. Consider adding a `--verbose` flag to `mklists run`.
