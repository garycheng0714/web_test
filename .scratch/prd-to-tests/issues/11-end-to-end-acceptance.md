# 11: End-to-end acceptance and docs

**What to build:** The whole pipeline works end to end on the sample PRD through the
documented commands: plan, approve, automate to green.

**Blocked by:** 09, 10 (the live pipeline already covers most of this ticket).

**Status:** needs-triage

- [ ] Running `plan` on the sample PRD, approving the cases, then running `automate` produces passing tests
- [ ] The approval gate is exercised (automate refuses before approval, proceeds after)
- [ ] Filtering by priority and type selects the expected subset of generated tests
- [ ] The command entrypoints and the one-time browser install step are documented in the repo's agent/README docs

## Comments

**2026-10-24 — metadata.** The old blocker 08 is wontfix/superseded. Plan -> gate -> automate has been exercised live (PR #13 and #22), so most of the acceptance is already proven; re-scope to filtering by priority/type and the remaining docs.
