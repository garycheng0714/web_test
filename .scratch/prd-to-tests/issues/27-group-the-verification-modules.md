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

**Status:** ready-for-agent

- [ ] The package has `__init__.py` and `__main__.py`; `uv run python -m web_test.planning.verify --help` works.
- [ ] The boundary model, prepare, run, and CLI no longer share one module; each has its own module.
- [ ] All production and test imports use the package paths; no flat `verify_*.py` imports remain.
- [ ] The verification input JSON, CLI flags, cache key, and published check behavior are unchanged.
- [ ] `uv run pytest`, `uv run basedpyright`, `uv run lint-imports`, and `actionlint` pass.
