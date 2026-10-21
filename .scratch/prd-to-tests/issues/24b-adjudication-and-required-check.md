# 24b: Adjudicate and require the verification check

**What to build:** Add human adjudication to the 24a check and make it required. An approving PR
review with a reason re-runs `NEEDS_REVIEW`/`BLOCKED` as success and records the original verdict;
`FAIL` has no routine override. Then enable the required check in branch protection.

**Blocked by:** 24a (shadow verification check).

**Status:** needs-triage

- [ ] An approving review with a reason re-runs `NEEDS_REVIEW`/`BLOCKED` as success
- [ ] The override records the original verdict, reason, and head SHA
- [ ] A new head voids the override and requires a fresh verdict
- [ ] `FAIL` ignores approvals; only admin break-glass can bypass it
- [ ] Branch protection requires the `verify-test-case` check
- [ ] Shadow-to-required rollout and the break-glass policy are documented
- [ ] Repeated runs update one result and do not add duplicate comments
- [ ] Verified live on a Test Case PR

## Out of scope

- The core shadow check, parser, and workflow wiring are 24a.
