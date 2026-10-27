# 04: Build a labeled verifier set

**What to build:** A versioned set of test-case artifacts labeled by the domain expert as PASS or
FAIL, with the expected failing dimension for each FAIL, split into train, dev, and test. This is
the ground truth that 05 and 06 consume; without it the verifier's verdicts cannot be trusted.

**Shape:**

- `LabeledSet` — Pydantic boundary, read from disk: `id`, `version`, `split`, `prds`, `cases`.
- `LabeledCase`: `id`, `prd_id`, `label` (`PASS`/`FAIL`), `expected_dimension` (required for
  `FAIL`), `artifact` (inline text or path), `notes`.
- Invariants: ids unique; train/dev/test disjoint; `expected_dimension` present iff `FAIL`;
  few-shot examples may come only from train; a case never moves between splits.

**Blocked by:** 03.

**Status:** ready-for-human

- [ ] 30–50 labeled case outputs as the first slice; 50 PASS + 50 FAIL is the stretch target
- [ ] Labels come from the domain expert, not from Jev or another model
- [ ] The test split is disjoint and is not looked at during dataset authoring
- [ ] Every FAIL names the dimension that should catch it
- [ ] The set is versioned and its hash is recorded by the eval
- [ ] A loader validates the split and refuses a leaked or missing test split
- [ ] The existing six cases are either re-labeled into the new set or kept as the dev baseline

## Decisions / assumptions

- A label describes one case output, not a whole PRD; a PRD can contribute several labels.
- Production adjudications from 01 are an optional input, not a prerequisite.
- The domain expert is the builder; no outsourcing.

## Out of scope

- Changing the question set (03 decides that first).
- Computing metrics (05).
