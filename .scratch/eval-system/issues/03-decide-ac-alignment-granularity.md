# 03: Decide AC alignment granularity

**What to build:** A recorded decision on whether AC alignment stays a case-level judgment or
becomes one question per AC (or per step) before the labeled set is built. The decision names the
cost in question count, the effect on the question-set version, and whether the existing bands can
be reused.

**Shape (only if split):** a new `CheckDimension` member and a question-id scheme; invariants:
exactly one question per AC or step; aggregation unchanged; existing dimensions untouched.

**Blocked by:** None (can start immediately).

**Status:** ready-for-human

- [ ] The decision is recorded with rationale and cost
- [ ] If kept: the limitation is written down and ticket 04 labels at case level
- [ ] If split: the question shape, id scheme, and version bump are specified
- [ ] The decision states whether the existing six-case fixture is re-labeled or retired

## Decisions / assumptions

- Changing the question set invalidates every existing label and calibration result.
- The decision must be made before 04, not after.
