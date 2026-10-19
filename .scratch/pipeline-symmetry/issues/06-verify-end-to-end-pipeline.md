# 06: Verify the end-to-end pipeline on GitHub

**What to build:** A real PRD PR merged into `main` produces an app-authored, CI-green test-case PR;
merging that produces an app-authored, CI-green tests PR. Both stages are exercised against the real
repository, with evidence recorded.

**Blocked by:** 03 (automation CI identity), 04 (plan in CI).

**Status:** ready-for-human

- [ ] The plan workflow is on `main`
- [ ] Merging an added `prd/**` PR produces a test-case PR authored by the app, with a real `ci` run
      that executed jobs
- [x] Merging that test-case PR produces a tests PR authored by the app, with a real `ci` run
- [x] Branch names show `<kind>/<id>-<run>-<attempt>`; commit and PR authors share the app identity
- [x] The `test` check gates the PR merge, while direct pushes to `main` still work
- [x] The verification PR numbers are recorded here

## Notes

- Human-run: it needs real merges, so it cannot be verified by unit tests.
- Record the PR numbers and any surprises (e.g. an app permission that turned out too narrow).

## Comments

Automation half verified. Merging the one-case smoke PR **#6** triggered `automate`, which opened
**PR #7** authored by `app/web-test-qa-flow` (commit `web-test-qa-flow[bot]`, branch
`automation/register-login-smoke-39221763763-1`); PR #7's `ci`/`test` executed and passed in 48s. PR
#6 itself had to pass its `test` check before it could be merged, confirming the required status check
gates PR merges. The plan half (a merged `prd/**` PR producing a test-case PR) still awaits ticket 04.
