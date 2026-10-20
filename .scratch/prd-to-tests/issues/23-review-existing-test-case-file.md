# 23: Review an existing Test Case file

**What to build:** A local command that reads a Test Case markdown file back into the review state
and runs the same Jev verification used during Plan. It compares the artifact digest with the
record's digest and reports `BLOCKED` with the reason `stale` when they differ, so a file edited
after Plan can be verified without re-planning the PRD.

**Blocked by:** 21 (record and digest).

**Status:** needs-triage

- [ ] A file produced by Plan round-trips back into step-level review state
- [ ] The parsed state preserves each step's action and expected result
- [ ] Editing a case, step, or expected result changes the verification result
- [ ] A digest mismatch is `BLOCKED` with the reason `stale`, not a pass or a separate status
- [ ] The command is read-only and usable outside CI
- [ ] Tests cover the round trip, an edit, and the stale path
