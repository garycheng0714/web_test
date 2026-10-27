# 08: Add a designer eval

**What to build:** A local command that runs the designer on a fixed set of PRDs N times per variant
and reports deterministic quality metrics: valid requirement ids, requirement coverage, case count,
test-type distribution, empty steps, and open-question count. No LLM judge in this slice.

**Shape:**

- Reuses `RunRecord` from 07.
- `DesignerDataset` — Pydantic boundary: `id`, `version`, `prds` (`id`, `text`, `requirements`).
- Invariants: every requirement id is unique per PRD; every case's `requirement_ids` is a subset of
  the PRD's ids; coverage is computed only from valid ids.

**Blocked by:** 07.

**Status:** ready-for-agent

- [ ] Five PRDs with numbered requirements, including the existing three
- [ ] Three runs per PRD per variant
- [ ] Metrics: valid ids, coverage, case count, type distribution, empty steps, open questions
- [ ] Invalid requirement ids are findings, not coverage
- [ ] The report shows per-PRD deltas and an aggregate with n
- [ ] The variant records model, skill digest, and instruction digest

## Decisions / assumptions

- Deterministic metrics first; grounding precision, duplicate rate, and atomicity need a judge or
  goldens and are out of scope.
- A PRD's requirements are the denominator; non-testable prose is excluded when the dataset is built.
- The existing test-case artifacts can seed the dataset, but the PRDs are the input.

## Out of scope

- A judge for grounding or atomicity.
- Golden test cases.
