# 27: Group the verification modules

**What to build:** Move the verification modules into a `web_test/planning/verify/` package, and
split the current CLI module into input, prepare, run, and CLI responsibilities. Keep
`python -m web_test.planning.verify prepare|run` working. Behavior, the verification input JSON, the
CLI flags, the cache key, and the published check are unchanged.

Target modules:

- `input.py`: `PreparedVerification`
- `prepare.py`: `prepare`
- `run.py`: `RunResult`, `run`
- `cli.py`: `main` and the file/output helpers
- `resolution.py`, `key.py`, `payload.py`, `cache.py`: the existing modules, moved
- `__main__.py`: package entrypoint

The workflow command stays `python -m web_test.planning.verify`.

**Blocked by:** None (can start immediately).

**Status:** ready-for-human (done; implemented)

- [x] The package has `__init__.py` and `__main__.py`; `uv run python -m web_test.planning.verify --help` works.
- [x] The boundary model, prepare, run, and CLI no longer share one module; each has its own module.
- [x] All production and test imports use the package paths; no flat `verify_*.py` imports remain.
- [x] The verification input JSON, CLI flags, cache key, and published check behavior are unchanged.
- [x] `uv run pytest`, `uv run basedpyright`, `uv run lint-imports`, and `actionlint` pass.

**2026-10-23 — implemented.** The verification code is now a package: `input`, `prepare`, `run`,
`cli`, `resolution`, `key`, `payload`, and `cache`, with `__main__.py` keeping
`python -m web_test.planning.verify` working. The boundary model, prepare, run, and CLI each live in
their own module; the workflow command, JSON, flags, key, and publish behavior are unchanged. 191
passed; basedpyright, lint-imports, and actionlint are green.

**2026-10-23 — tracker cleanup.** All acceptance items are checked; status moved to `ready-for-human`.

## Comments

**2026-10-24 — bookkeeping: done.**

`web_test/planning/verify/` is a package (`input`, `prepare`, `run`, `cli`, `resolution`, `key`, `payload`, `cache`). Status → `ready-for-human (done; implemented)`.
