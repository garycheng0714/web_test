# 28: Split the verification tests by phase

**What to build:** Split the 592-line `test_verify.py` by responsibility: prepare, run, cache, and
CLI. Move the shared test helpers (case builders, fake `SystemOne` callables, the publish sink, the
ready input, and the run-payload helper) into one helper module. Reuse those helpers in the
resolution and key tests to remove duplicated case/file builders. Production code does not change.

**Blocked by:** 27 (the package import paths must exist first).

**Status:** ready-for-agent

- [ ] `test_verify.py` is removed; prepare, run, cache, and CLI tests live in separate files.
- [ ] Shared helpers are defined once; the resolution and key tests use them.
- [ ] No test coverage or assertion is dropped; the suite count stays at least 191.
- [ ] `uv run pytest`, `uv run basedpyright`, `uv run lint-imports`, and `actionlint` pass.
