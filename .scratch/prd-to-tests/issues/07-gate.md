# 07: Gate

**What to build:** The human approval gate as a state on the test-case artifact plus a
reusable check. Approval is expressed by editing the artifact's `Status` line (no separate
command).

**Blocked by:** 05

**Status:** ready-for-agent

- [ ] The test-case document carries an explicit approval state with defined values (unapproved → approved)
- [ ] A pure function reports whether the document is approved
- [ ] The function's behavior is unit-tested for both states
- [ ] Approval by editing the state line is documented
