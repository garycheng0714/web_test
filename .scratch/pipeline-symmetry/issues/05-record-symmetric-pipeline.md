# 05: Record the symmetric pipeline decision

**What to build:** The spec, an ADR, the glossary, and the superseded plan ticket describe the
symmetric pipeline that tickets 03 and 04 build: both stages are merge-triggered CI workflows running
under one app identity, with run-scoped branches, and the human Gate (merging the test-case PR) is
unchanged.

**Blocked by:** 03 (automation CI identity), 04 (plan in CI).

**Status:** ready-for-agent

- [ ] The spec's "pipeline shape / where it runs" describes `plan` running in CI, triggered by a
      merged PRD, and no longer "may run locally"
- [ ] A new ADR records the symmetry, the shared app identity, and run-scoped branch names
- [ ] The plan ticket's "local first / no CI workflow for plan" note is marked superseded
- [ ] The glossary's Gate entry states whether a PRD merge is itself a gate
- [ ] The written decisions match what 03 and 04 actually shipped

## Notes

- Keep the ADR short; it records a decision, not a tutorial.
