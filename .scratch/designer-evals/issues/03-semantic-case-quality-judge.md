# 03: Add a semantic judge for designer claim alignment

**What to build:** One binary judge for one semantic failure mode: whether a generated case
actually tests the requirement it claims, with every behaviour assertion traceable to the PRD.
Input: the whole PRD plus the case. Output: `{critique, result}` with Pass/Fail, critique first.
Validate against the human `claim_alignment` labels from ticket 02; report TPR/TNR and a CI.
Report-only; no gate.

**Blocked by:** 02 (done). Validation is additionally blocked on more PRDs — see Next steps.

**Status:** needs-triage

**Shape:**
- Types: `ClaimJudgement` (claim_id, requirement_id, case_id, verdict, critique),
  `JudgeReport`.
- Boundary: judge prompt + JSONL outputs under `evals/designer/judge/`; judge results
  may also be written as `LLM` annotations on the claim spans.
- Invariants: one failure mode per judge; binary Pass/Fail; critique before result; one
  judgement per claim span; few-shot only from train PRDs; no dev/test leakage; human labels
  remain the ground truth. Input is the **whole PRD plus the case**: judging
  `undefined_behavior` needs the full PRD, and `wrong_assertion_to_requirement` needs the
  claimed FR's body and AC. The target is `claim_alignment`; `claim_failure_mode` and
  `claim_reason` are human analysis fields and are not predicted by the judge.

## Tasks

- [x] Pin the judged criterion: fail when the case's steps are off-scenario, when a behaviour
      assertion is absent from the whole PRD or cannot be decided at all, when it does not verify
      the claimed FR's body or AC, or when the claimed FR has no scenario of its own and only
      rides on another FR's case (`duplicated`). The judge does not predict the mode.
- [x] Write the judge prompt with criterion, Pass/Fail definitions, few-shot from train
      PRDs only, and structured output with critique first.
- [ ] Build a claim-level train/dev/test split by PRD. Blocked: only one labeled PRD; the dev run
      uses the 31 house claims as a claim-level sample.
- [x] Run on dev; measure TPR/TNR + Wilson/bootstrap CI; inspect disagreements.
- [ ] Iterate on dev; run test once. Blocked on label stability (see the dev run below).
- [x] Write judge results as JSONL; `LLM` annotations are still optional. Export them alongside
      human labels.
- [ ] Compare with claim coverage: does the judge catch what the tags miss?
- [x] Add tests for the parser, prompt, metrics, and the agent output.

## Out of scope

- Other semantic modes (observable, continuity, hallucination).
- Gate changes.
- Phoenix experiments (ticket 04).
- Using the Jev verifier as ground truth: it is the gate, so it is circular.

## Risks

- Small PRD sample; wide CIs.
- `wrong_scenario_to_requirement` has only 5 labels in the automationexercise run (2 from one
  case), so that class's TPR is unusable; add PRDs or synthetic negatives before trusting it.
- Label semantics mix alignment and grounding: a fail can mean the case tests the wrong FR or
  that it asserts behaviour the PRD never defines. Report per-mode counts; do not read the
  aggregate fail rate as one signal.
- `undefined_behavior` merges two causes (PRD missing, or assertion too vague), so its count
  conflates a PRD gap with a vague assertion; `claim_reason` keeps the distinction.
- `duplicated` is a claim-level signal about case granularity, not about a wrong assertion:
  `case_duplicate` (CODE) compares whole cases, while `duplicated` says one FR has no distinct
  scenario inside a multi-FR case. The fix is to split the case (ticket 30).
- The judge may repeat the designer's blind spots; human labels are required.
- Model cost per run.
- Judge annotations can drift from the exported JSONL; treat the snapshot as the metric input.

## Evidence from the first labeled run (2026-10-29)

Run `old-skill-units-automationexercise-20261029` (old vendored skill, not the house skill):
27 requirements, 43 cases, 54 claims, all HUMAN-labeled; see
`old-skill-runs/old-skill-automationexercise-20261029/report.md`.

```text
54 claims -> 5 wrong_scenario (91% aligned)
          -> 16 grounding failures (undefined 9, wrong_assertion 7)
          -> 33 clean (61%)
tested 27/27   clean 21/27 (78%, Wilson CI 0.59-0.89)
```

- The failing class is assertion discipline, not claim tagging: every requirement is exercised,
  and the 6 requirements without a passing claim each have a case that only fails on an extra
  assertion.
- 4 of the 9 `undefined_behavior` labels contradict the designer's own `open_questions`
  (`case-34` vs #18 cart cleared, `case-33` vs #13 invoice contents, `case-20` vs #6 grand
  total, `case-11` vs #5 quantity rules). That points at the skill's coverage checklist, not
  model hallucination.
- There is no house-skill run on this PRD yet, so the 39% fail rate is not evidence about the
  house designer before the control run below.

## House-skill control run (2026-10-29)

Run `house-automationexercise-20261029` on the same PRD, 31 claims, all HUMAN-labeled; see
`runs/house-automationexercise-20261029/report.md`.

```text
                    old skill     house skill
cases                  43             23
claims                 54             31
fail                 21 (39%)       6 (19%)
tested               27/27          26/27
clean                21/27 (78%)    23/27 (85%, CI 0.68-0.94)
failure modes   undefined 9     undefined 1
                wrong_assertion 7  wrong_assertion 2
                wrong_scenario 5   wrong_scenario 1
                -                  duplicated 2
```

- The house rules are the fix for over-assertion: `undefined_behavior` 9 -> 1 and
  `wrong_assertion` 7 -> 2. The old-skill run is now the negative set for that mode.
- The house suite does not win on every axis. It loses `FR-UI-02` entirely (home accessibility),
  because "keep the suite small and dense" dropped it, and it introduces `duplicated` (2): multi-FR
  cases where one FR has no scenario of its own (`case-12`, `case-18`). Ticket 30 covers that
  policy boundary; the fix is splitting cases, not reverting to the old behaviour.
- Negatives for the judge: 6 in the house run, 21 in the old run. Neither supports a by-PRD
  TPR/TNR split on its own.
- The PRD was normalized after this comparison (2026-10-30): `FR-ACC-01/02` merged, `FR-UI-02`
  removed, `FR-ENG-02` narrowed to Home. Requirements are now 25, so the 27-FR numbers above are
  the pre-normalization baseline; future runs are not directly comparable per FR.

## Judge implementation and dev run (2026-11-02)

- `evals/designer/judge.py` + `designer_eval/judge.py`: one binary judgement per labeled claim,
  whole PRD + case, critique first. Model: `WEB_TEST_JUDGE_MODEL` (default
  `openai-chat:kimi-k2.7-code`, a different family from the designer).
- Dev fixture `evals/designer/judge/data/`: 85 automationexercise claims + 7 register-login
  claims, with the PRD text from before the normalization. The run directories stay local.
- Dev run on the 31 house claims: **TPR 0.33 [0.10, 0.70], TNR 0.88 [0.70, 0.96]**, 7
  disagreements.
- Most disagreements are label-boundary inconsistencies, not prompt failures:
  - `ORD-04` invoice content fails, but `CART-02` total price = 4x passes; both assert a value the
    PRD never states.
  - `ORD-01` address block fails, but `ORD-02` comment carried passes.
  - `PRD-01` detail-page assertions fail, but `UI-01` cart-page scroll passes.
  - The old-skill and house labels disagree on `case-18 -> CART-01` (pass vs `duplicated`).
- Next: write one explicit rule per failure mode, re-label the 31 house claims, then tune the
  prompt. The current dev metrics are not a reliable judge estimate.

## Next steps

1. **House-skill control run (done).** See the section above. The remaining designer work is
   ticket 30 (split multi-FR cases) and the open-questions self-check (step 2).
2. **Skill self-check ticket (separate from this one).** Add a rule that anything listed in
   `open_questions` may not appear as an `expected_result`, and require each behaviour assertion
   to cite an `FR-*` or PRD section. The spec's non-goal keeps designer changes out of this
   ticket; open it separately and measure the delta with step 1.
3. **More PRDs before any TPR/TNR claim.** A by-PRD split needs at least 5-6 PRDs; with three
   (one of which is this 27-FR PRD) the test split is a single PRD. Until then the judge is
   report-only: write it, run it, but do not publish TPR/TNR or gate on it.

## Comments

Renumbered from the old ticket 02 on 2026-10-29. Now depends on the human labels exported by
ticket 02.

2026-10-29: ticket 02 labels are complete for the automationexercise run (54/54 claims, three
HUMAN configs). Evidence and next steps above are based on that run's `report.md`.
