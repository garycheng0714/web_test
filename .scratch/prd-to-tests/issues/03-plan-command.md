# 03: Stage 1 `plan` — PRD to test cases

**What to build:** A `plan` subcommand that reads a PRD file and, acting as a QA engineer,
writes a structured test-case document. Running it on the checked-in sample PRD produces
reviewable coverage. This ticket is independent of the Node workspace.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] `plan --prd <path>` is a required-argument command
- [ ] The PRD is read as markdown or plain text
- [ ] A QA test-designer agent derives one case per applicable technique (happy, negative/validation, boundary/equivalence) per requirement, without padding
- [ ] Each case records: id, source requirement id(s), priority (P1–P3), type (happy/negative/boundary), preconditions, Given/When/Then steps, expected result
- [ ] Requirement IDs are assigned when the PRD lacks them, and a requirement-to-case mapping is written
- [ ] Duplicate scenarios across requirements are merged while keeping all source requirement references
- [ ] The document records the application base URL and starts in a draft approval state
- [ ] A small sample PRD is checked into the repo for acceptance and practice
- [ ] Agent-level tests override the model and assert the produced document (coverage, traceability, dedup, IDs)
