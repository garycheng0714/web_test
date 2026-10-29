# 03: Add a semantic judge for designer case quality

**What to build:** One binary judge for one semantic failure mode: whether a generated case
actually tests the requirement it claims. Input: the PRD requirement text + the case. Output:
`{critique, result}` with Pass/Fail, critique first. Validate against the human
`case_alignment` labels from ticket 02; report TPR/TNR and a CI. Report-only; no gate.

**Blocked by:** 02.

**Status:** needs-triage

**Shape:**
- Types: `CaseJudgement` (case_id, requirement_id, verdict, critique), `JudgeReport`.
- Boundary: judge prompt + JSONL outputs under `.scratch/designer-evals/judge/`; judge results
  may also be written as `LLM` annotations on the case spans.
- Invariants: one failure mode per judge; binary Pass/Fail; critique before result; few-shot
  only from train PRDs; no dev/test leakage; human labels remain the ground truth.

## Tasks

- [ ] Choose the one mode: AC alignment ("case does not test its claimed requirement").
- [ ] Write the judge prompt with criterion, Pass/Fail definitions, few-shot from train
      PRDs only, and structured output with critique first.
- [ ] Split by PRD: train, dev, frozen test set.
- [ ] Run on dev; measure TPR/TNR + Wilson/bootstrap CI; inspect disagreements.
- [ ] Iterate on dev; run test once.
- [ ] Write judge results as `LLM` annotations and/or JSONL; export them alongside human
      labels.
- [ ] Compare with the code coverage tags: does the judge catch what the tags miss?
- [ ] Add tests for the parser and metrics.

## Out of scope

- Other semantic modes (observable, continuity, hallucination).
- Gate changes.
- Phoenix experiments (ticket 04).
- Using the Jev verifier as ground truth: it is the gate, so it is circular.

## Risks

- Small PRD sample; wide CIs.
- The judge may repeat the designer's blind spots; human labels are required.
- Model cost per run.
- Judge annotations can drift from the exported JSONL; treat the snapshot as the metric input.

## Comments

Renumbered from the old ticket 02 on 2026-10-29. Now depends on the human labels exported by
ticket 02.
