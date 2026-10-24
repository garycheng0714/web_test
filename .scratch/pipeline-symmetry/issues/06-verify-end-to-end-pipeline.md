# 06: Verify the end-to-end pipeline on GitHub

**What to build:** A real PRD PR merged into `main` produces an app-authored, CI-green test-case PR;
merging that produces an app-authored, CI-green tests PR. Both stages are exercised against the real
repository, with evidence recorded.

**Blocked by:** 03 (automation CI identity), 04 (plan in CI).

**Status:** ready-for-human (done; verified live)

- [x] The plan workflow is on `main`
- [x] Merging an added `prd/**` PR produces a test-case PR authored by the app, with a real `ci` run
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

Plan half verified too. `plan.yml` landed on `main` as `9defae0`. Merging **PR #8** (added
`prd/login-smoke.md`) triggered `plan` run **39227687708** (green, 38s, printed `planned`), which
opened **PR #9** authored by `app/web-test-qa-flow`, branch `plan/login-smoke-39227687708-1`, adding
`test-case/test-case-login-smoke.md` with 2 cases. PR #9's `ci`/`test` **executed and passed** (53s),
and its body carried the Jev review (`Groundedness: 2/2 grounded`). PR #9 was closed unmerged as a
verification artifact (merging it would have triggered `automate`) and its branch deleted.

Both stages are now symmetric: merged `prd/**` → app-authored test-case PR; merged `test-case/**` →
app-authored tests PR; both run-scoped and both CI-tested.

One surprise: `actionlint` 1.7.12 reports `create-github-app-token@v3` as missing `app-id` /
not defining `client-id`. Its bundled metadata is stale — the action's real `action.yml` accepts
`client-id` and deprecates `app-id`. The warning also fires on the pre-existing `automate.yml`, so it
is a false positive, not a defect in either workflow.

**2026-10-24 — bookkeeping: done.**

Both stages were exercised live (PR #11, #13, #22; automate runs 39986654910 and 40055442740). Status → `ready-for-human (done; verified live)`.
