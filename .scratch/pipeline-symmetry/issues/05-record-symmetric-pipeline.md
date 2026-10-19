# 05: Record the symmetric pipeline decision

**What to build:** The spec, an ADR, the glossary, and the superseded plan ticket describe the
symmetric pipeline that tickets 03 and 04 build: both stages are merge-triggered CI workflows running
under one app identity, with run-scoped branches, and the human Gate (merging the test-case PR) is
unchanged.

**Blocked by:** 03 (automation CI identity), 04 (plan in CI).

**Status:** ready-for-human

- [x] The spec's "pipeline shape / where it runs" describes `plan` running in CI, triggered by a
      merged PRD, and no longer "may run locally"
- [x] A new ADR records the symmetry, the shared app identity, and run-scoped branch names
- [x] The plan ticket's "local first / no CI workflow for plan" note is marked superseded
- [x] The glossary's Gate entry states whether a PRD merge is itself a gate
- [x] The written decisions match what 03 and 04 actually shipped

## Comments

Written. Added `docs/adr/0008-both-stages-in-ci-under-one-app-identity.md` (symmetric pipeline, one
app identity, run-scoped branches, base URL from the repository variable, Gate unchanged). Updated
the spec's banner, "Where it runs", "PRD input" and Out-of-Scope bullet; marked ticket 13's
"Local vs CI" and "A CI workflow for plan (local first)" as superseded (and noted that its
`plan/<prd-stem>-<UTCstamp>` branch shape was replaced by ticket 02). `CONTEXT.md`'s Gate entry now
states that a PRD merge is not a gate and fixes the artifact path to
`test-case/test-case-<prd-stem>.md`. Also fixed `README.md`, which still claimed the default
`GITHUB_TOKEN` and omitted `plan.yml`.

The decisions match 03/04 as shipped: `plan.yml` and `automate.yml` both mint an app token, both run
with `contents: read`, both act on exactly one added file, and both take their suffix from
`WEB_TEST_RUN_ID`/`WEB_TEST_RUN_ATTEMPT` via `web_test/naming.py`. Verified live in ticket 06.

## Notes

- Keep the ADR short; it records a decision, not a tutorial.
