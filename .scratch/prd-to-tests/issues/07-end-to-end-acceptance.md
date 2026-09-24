# 07: End-to-end acceptance and docs

**What to build:** The whole pipeline works end to end on the sample PRD through the
documented commands: plan, approve, automate to green. The repo's documentation names the
commands.

**Blocked by:** 05, 06

**Status:** ready-for-agent

- [ ] Running `plan` on the sample PRD, approving the cases, then running `automate` produces passing Playwright tests
- [ ] The approval gate is exercised (automate refuses before approval, proceeds after)
- [ ] Tag filtering selects the expected subset of generated tests
- [ ] The command entrypoints and the one-time browser install step are documented in the repo's agent/README docs
