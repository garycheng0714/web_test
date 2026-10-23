# 02: Run-scoped branch names shared by both stages

**What to build:** Both pipeline stages name their branch with the same shape and a run-scoped suffix:
`<kind>/<id>-<run_id>-<run_attempt>` (e.g. `plan/register-login-…`, `automation/test-case-0001-…`).
Re-running a job can never collide on push, and the two stages stop drifting apart. When run info is
absent (a local run), a UTC timestamp is used instead.

**Blocked by:** None (can start immediately).

**Status:** ready-for-human

- [x] Plan and automation branches are produced by one shared naming rule, not two divergent ones
- [x] The suffix uses the GitHub run id and attempt when supplied by the environment
- [x] A local run without run info falls back to a UTC timestamp
- [x] Unit tests cover the shared shape, the run-scoped suffix, and the local fallback
- [x] `uv run pytest` is green

## Comments

Implemented: `web_test/naming.py` (`run_token`, `branch_for`); both stages build `<kind>/<id>-<token>`;
`WEB_TEST_RUN_ID`/`WEB_TEST_RUN_ATTEMPT` in CI, a UTC timestamp locally. Committed as
"Name branches from the CI run, shared by both stages". `uv run pytest`: 103 passed, 1 skipped.

## Notes

- This is a prefactor: apart from branch names, behaviour does not change.
- The automation branch is currently fixed (`automation/<id>`) and the plan branch is timestamped;
  this ticket makes both run-scoped.

**2026-10-23 — tracker cleanup.** All acceptance items are checked; status moved to `ready-for-human`.
