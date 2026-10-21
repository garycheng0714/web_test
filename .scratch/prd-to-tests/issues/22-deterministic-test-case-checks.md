# 22: Add deterministic checks for Test Case structure

**Deferred:** Not part of v1. The v1 contract explicitly covers grounded/complete only; this ticket
extends the claim to structural validity after 21 and 24b are live.

**What to build:** Checks that need no model judgment run alongside verification and land in the
same record: front-matter and required fields, unique case identifiers, requirement IDs that exist in
the PRD, a happy-path case per requirement, and steps with non-empty actions and expected results.
Counts stay in code.

**Blocked by:** 21 (record shape and rendering).

**Status:** needs-triage

- [ ] A malformed or incomplete Test Case file is flagged without calling Jev
- [ ] Requirement-to-case coverage is computed in code, not asked as a model question
- [ ] Each deterministic result appears in the same record and PR body section as Jev results
- [ ] Checks are pure functions over the artifact and PRD text
- [ ] Tests cover each failure and the clean case
