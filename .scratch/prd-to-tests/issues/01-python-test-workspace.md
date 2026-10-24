# 01: Python test workspace

**What to build:** A pytest + Playwright Python workspace, so our own tests and the generated
automation tests can run. No Node workspace.

**Blocked by:** None (can start immediately)

**Status:** ready-for-human (done; implemented)

- [x] pytest is configured; Playwright's Python bindings are installed via uv
- [x] `uv run pytest` runs an existing trivial test and passes
- [x] The one-time browser install step is documented
- [x] No Node/TypeScript toolchain is introduced

## Comments

Implemented. Added `pytest` + `playwright` + `pytest-playwright` to the `dev` dependency
group, a `[tool.pytest.ini_options] testpaths = ["tests"]` config, a browser-launch smoke test
(`tests/test_workspace.py`), and setup/install docs in `README.md`. `uv run pytest` passes
(1 test). No Node toolchain introduced. Code review (Standards + Spec) surfaced a broken
`--browser firefox` example (only chromium was installed) and a stale "no tests configured"
line in `AGENTS.md`; both fixed.

**2026-10-24 — bookkeeping: done.**

`pyproject.toml` carries pytest, playwright, and pytest-playwright; the suite runs. Status → `ready-for-human (done; implemented)`.
