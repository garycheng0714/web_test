# 14: Report coverage in CI

**What to build:** Add a coverage report to the existing test job. Report only: no threshold, so the
check cannot fail the build. Record the first baseline.

**Blocked by:** None.

**Status:** ready-for-human (done; threshold decision open)

- [x] Add `pytest-cov` as a dev dependency
- [x] Add the coverage flags to the `test` job
- [x] Add the command to `AGENTS.md` and `README.md`
- [x] Keep it report-only (no `--cov-fail-under`)
- [x] Record the baseline

## Comments

**2026-10-21 — implemented.**

- `test` job now runs `uv run pytest -q --cov=web_test --cov-report=term-missing`. Coverage is
  folded into the existing job so the Chromium install is not duplicated.
- Baseline: **91%** (1103 statements, 100 missed), 138 passed, 1 skipped.
- No threshold. The automation paths are exercised against a live site, so a coverage trend is
  informative rather than a merge gate. The remaining human decision is whether to require a
  threshold later.

**2026-10-24 — bookkeeping: done.**

`ci.yml` runs pytest with `--cov=web_test --cov-report=term-missing`. The open item is whether to set a threshold. Status → `ready-for-human (done; threshold decision open)`.
