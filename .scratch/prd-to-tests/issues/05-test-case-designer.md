# 05: Test Case designer and test-case artifact

**What to build:** A Pydantic AI agent that consumes the `PRD` model and produces the
structured test-case document, plus the document's format.

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] One case per applicable technique (happy, negative/validation, boundary/equivalence) per requirement, without padding
- [ ] Each case records: id, source requirement id(s), priority, type, preconditions, Given/When/Then steps, expected result
- [ ] Priority and type use constrained (enum) values
- [ ] A case may reference multiple requirements; duplicate scenarios are merged while keeping all source requirement references
- [ ] A requirement-to-case mapping is written
- [ ] The document carries the base URL and starts in an unapproved (`draft`) state
- [ ] Agent-level tests override the model and assert the produced document (coverage, traceability, dedup, ids)
