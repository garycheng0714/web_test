# 28: Split the verification tests by phase

**What to build:** Split the 592-line `test_verify.py` by responsibility: prepare, run, cache, and
CLI. Move the shared test helpers (case builders, fake `SystemOne` callables, the publish sink, the
ready input, and the run-payload helper) into one helper module. Reuse those helpers in the
resolution and key tests to remove duplicated case/file builders. Production code does not change.

**Blocked by:** 27 (the package import paths must exist first).

**Status:** ready-for-human (done; implemented)

- [x] `test_verify.py` is removed; prepare, run, cache, and CLI tests live in separate files.
- [x] Shared helpers are defined once; the resolution and key tests use them.
- [x] No test coverage or assertion is dropped; the suite count stays at least 191.
- [x] `uv run pytest`, `uv run basedpyright`, `uv run lint-imports`, and `actionlint` pass.

**2026-10-23 — implemented.** `test_verify.py` is split into prepare, run, cache, and CLI test
modules. `verify_helpers.py` holds the case builders, fake `SystemOne` callables, publish sink,
ready input, and run-payload helper; the resolution and key tests use it. The suite still has 191
passing tests, and basedpyright, lint-imports, and actionlint are green.

**2026-10-23 — tracker cleanup.** All acceptance items are checked; status moved to `ready-for-human`.

## Comments

**2026-10-24 — bookkeeping: done.**

The verification tests are split into prepare, run, cache, and CLI modules. Status → `ready-for-human (done; implemented)`.
