# 04: Compare designer runs in Phoenix experiments

**What to build:** A Phoenix dataset of the pinned PRDs and an experiment wrapper that runs
`design_test_cases` and records code evaluator results, so two or more runs can be compared in
the Phoenix experiments UI. The experiment is a review aid; it does not gate merges.

**Blocked by:** 01 (eval units). 02 optional for human-label comparison.

**Status:** needs-triage

**Shape:**
- Types: dataset examples (PRD input + metadata), experiment task output (`DesignOutput`),
  evaluator results. No new production module.
- Boundary: Phoenix dataset and experiment records; run metadata includes model, prompt
  version, and `designer.run.id`.
- Invariants: dataset examples are pinned to the PRD set; experiment names include model/run
  identity; evaluator names stay stable across runs; no required check or gate.

## Tasks

- [ ] Create or reuse a Phoenix dataset with one example per pinned PRD.
- [ ] Wrap `design_test_cases` as the experiment task; persist model and run metadata.
- [ ] Add code evaluators: requirement coverage, invented IDs, empty IDs, duplicate cases.
- [ ] Run two experiments with a controlled change (model or prompt) and compare them in the
      UI.
- [ ] Keep human labels in the annotation/export path; do not let experiment evaluators
      replace them.
- [ ] Document the runbook, cost, and how to reset the dataset.
- [ ] Run `uv run ruff check --select F401` for any new scripts.

## Out of scope

- CI or gate changes.
- Semantic judge (ticket 03; may be added later).
- Changing the designer prompt/model.
- Production monitoring.

## Risks

- Experiment task may run the designer once per example; model cost depends on dataset size.
- Experiment evaluators can duplicate the file-based metrics; keep one source of truth for
  each number.
- Phoenix experiments UI may not show human annotations alongside evaluator scores; verify
  before investing in the workflow.

## Flow

```text
PRD dataset
  │
  ▼
run_experiment(task=design_test_cases)
  │
  ├─ run A: model/prompt A
  └─ run B: model/prompt B
  │
  ▼
Phoenix experiment comparison
```

## Comments

Created 2026-10-29 from `.scratch/designer-evals/spec.md`.
