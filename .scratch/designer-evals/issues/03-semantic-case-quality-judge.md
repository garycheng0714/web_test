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
      assertion is absent from the whole PRD or cannot be decided at all, or when it does not
      verify the claimed FR's body or AC. `duplicated` moved to CODE (`case_duplicate`), because
      it is a structural property of the case, not a semantic judgement. The judge does not
      predict the mode.
- [x] Write the judge prompt with criterion, Pass/Fail definitions, few-shot from train
      PRDs only, and structured output with critique first. Few-shot is still blocked: there is
      no train PRD.
- [ ] Build a claim-level train/dev/test split by PRD. Blocked: only one labeled PRD; the dev run
      uses the 49 single-requirement claims (18 fail, 31 pass) from both source runs.
- [x] Run on dev; measure fail recall / pass specificity + Wilson CI; inspect disagreements.
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
- Judge annotations can drift from the exported JSONL; treat the committed dev set as the metric
  input, and note that Phoenix still holds the pre-alignment labels.

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

## Criterion revision and noise floor (2026-11-03)

- Prompt: one criterion (every behaviour assertion is stated in the PRD and verifies the claimed
  FR), step audit kept, `duplicated` moved to CODE, teardown and logout steps named as non-assertions.
- Input: the 50 single-requirement claims (18 fail, 32 pass). Model `openai-chat:deepseek-v4-pro`.
- Same prompt, three runs:

| run | fail recall | pass specificity | disagreements |
| --- | --- | --- | --- |
| 1 | 0.78 [0.55, 0.91] | 0.75 [0.58, 0.87] | 12 |
| 2 | 0.78 [0.55, 0.91] | 0.72 [0.55, 0.84] | 13 |
| 3 | 0.72 [0.49, 0.88] | 0.81 [0.65, 0.91] | 11 |

- Noise floor: fail recall moves 0.06 across runs, pass specificity 0.09, disagreements span 11 to
  13. A prompt change smaller than that is not attributable to the prompt. The earlier 0.33 to 0.78
  move is far above the floor, so that part is real.
- Of the 50 claims, 9 are wrong in all three runs and 7 flip. Six of the 7 flips are false alarms on
  passing claims, so the instability sits on the pass boundary; fail recall is the stable one.
- The 5 stable false alarms split along one rule, not one shape:
  - `case-14 -> FR-PRD-04` (the category page must list matching products), `case-21 -> FR-CART-02`
    (total = 4 x unit price) and `case-30 -> FR-ORD-02` (review rows must list name and price)
    assert content the snapshot PRD never states. Relabeled to `fail` on 2026-11-03.
  - `case-12 -> FR-PRD-03` (a second keyword restates AC2) and `case-6 -> FR-ACC-04` (a
    parenthetical rationale) restate a stated rule, so they stay `pass`. The judge was over-strict
    there, and the prompt now says that a repeated rule on a new input and an explanatory
    parenthetical are not assertions.
- The contradiction was `case-14 -> FR-CART-02` (fail) against `case-21 -> FR-CART-02` (pass): same
  requirement, same "total = 4 x unit price" assertion. Both are now `fail`.
- The 4 stable misses are `case-20` (wrong_assertion), `case-23`, `case-38` (undefined) and
  `case-43` (wrong_scenario).
- `case-23` and `case-33` (invoice content) are not PRD gaps to fix here: PRD section 11.2 item 9
  declares invoice format and content undefined, and item 6 does the same for upload limits. The
  right fix is that the designer must not assert them, which is the skill self-check ticket below,
  not a PRD edit.
- The cart total was the one genuine PRD gap. FR-CART-01 now has AC3 (`total price = price x
  quantity`). The fixture PRD was later aligned to v0.4, and the two `total` claims stay `fail` as
  `wrong_assertion_to_requirement`: the value is now defined, but it still does not verify
  FR-CART-02. A designer re-run is what measures the PRD change itself.
- Expect the next measurement to move: 3 relabels raise fail recall on those rows, and the
  prompt tolerance should remove 2 false alarms.

### PRD v0.4 alignment (2026-11-03)

The fixture PRD and every row's `requirement_text` now match the working PRD v0.4, so the dev set
describes the same product the designer reads. 82 rows remain (49 single-requirement, 18 fail).

- Dropped: `case-43 -> FR-UI-02` (requirement removed in v0.3), and the two multi-requirement
  `FR-ACC-02` rows whose case already had a merged `FR-ACC-01` claim.
- Remapped: one single-requirement row from `FR-ACC-02` to `FR-ACC-01`; its case yaml still cites the
  pre-merge id because the case is the artifact under test.
- Flipped to `pass`: `case-13 -> FR-PRD-04`, `case-14 -> FR-PRD-04`, because v0.4 states that the
  category page lists only the selected subcategory's products.
- Mode changed, verdict unchanged: `case-14 -> FR-CART-02`, `case-21 -> FR-CART-02` moved from
  `undefined_behavior` to `wrong_assertion_to_requirement`.

Phoenix still holds the original annotations, so a re-export reverts all of the above.

### Stability at temperature 0 (2026-11-03)

Question: is the flakiness sampling noise that a fixed temperature removes?

Method: the 7 claims that flipped across the three v4 runs, judged three more times with
`--temperature 0` on `deepseek-v4-pro` (21 calls).

| claim | human | default x3 | temp 0 x3 |
| --- | --- | --- | --- |
| `case-8 -> FR-PRD-03` | pass | pass fail fail | fail fail fail |
| `case-10 -> FR-PRD-01` | pass | fail fail pass | fail pass fail |
| `case-10 -> FR-PRD-05` | pass | fail pass pass | pass pass pass |
| `case-13 -> FR-CART-01` | pass | fail pass fail | fail fail pass |
| `case-15 -> FR-CART-03` | pass | fail pass fail | pass pass fail |
| `case-17 -> FR-ENG-01` | pass | pass fail pass | pass pass fail |
| `case-20-ui -> FR-UI-01` | fail | pass fail pass | fail pass pass |

- Temperature 0 does **not** make the judge deterministic. 5 of 7 still flip.
- The 2 that stopped flipping converged on the wrong verdict (`case-8`, `case-10 -> FR-PRD-05`), so
  stability bought nothing.
- Accuracy on this deliberately hard subset is 9/21 at the default and 10/21 at temperature 0. The
  pass boundary is ambiguous to the model, not merely noisy.
- Decision: keep the provider default temperature. Report a majority of three runs instead of one.
  `--temperature` and `--claim-id` stay in the CLI for experiments.

### Model choice (2026-11-03)

Compared on the pre-alignment 50-claim set, before the v0.4 label change:

| model | runs | fail recall | pass specificity | stable errors |
| --- | --- | --- | --- | --- |
| `deepseek-v4-pro` | 3 | 0.81 to 0.86 | 0.86 to 0.90 | 3 |
| `kimi-k2.7-code` | 2 | 0.81 | 0.83 to 0.86 | 6 |

`kimi` did not fix anything `deepseek` got wrong; its stable errors were a strict superset (the same
three plus `case-8`, `case-15` and `case-20-ui`). All three shared errors are the claims already
known to be label or PRD problems, so they say nothing about the model.

Decision: the default still moves to `kimi-k2.7-code`, because the judge must come from a different
family than the designer and the measured gap sits inside the noise floor. This is a choice for the
family rule, not evidence that kimi judges better. Revisit if a second labeled PRD shows a real gap.

### Strict rule applied, re-measurement (2026-11-03)

Rubric: an assertion must be derivable from the claimed FR's body or AC. Repeating a stated rule
with a new input, and an explanatory parenthetical, are not assertions. Both are in `spec.md` and
in the prompt.

Three runs on the corrected set (21 fail, 29 pass):

| run | fail recall | pass specificity | disagreements |
| --- | --- | --- | --- |
| 1 | 0.81 [0.60, 0.92] | 0.86 [0.69, 0.95] | 8 |
| 2 | 0.86 [0.65, 0.95] | 0.90 [0.74, 0.96] | 6 |
| 3 | 0.81 [0.60, 0.92] | 0.90 [0.74, 0.96] | 7 |

- Stable disagreements fell from 9 to 3, and all three are judge misses (`case-23`, `case-38`
  `undefined`; `case-43` `wrong_scenario`). No stable false alarm on a passing claim remains.
- The tolerance hit both targets: `case-12` and `case-6` pass in all three runs.
- The three relabeled claims fail in all three runs.
- All 7 remaining disagreements are flip-flops on passing claims.
- Attribution caveat: labels and prompt changed together, so the rate deltas are not a clean A/B.
  Only the per-claim predictions are attributable, because each was stated before the run.
- New noise floor for the next comparison: recall 0.05, specificity 0.04, 6 to 8 disagreements.
- Still dev-only and one PRD. Below the `validate-evaluator` target of 90 / 90; recall only just
  clears its 80 floor.

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
4. **Label boundary (resolved 2026-11-03).** The "assertion the PRD never states" rule is strict:
   relabel and fail. Two exceptions are written into the spec and the prompt: repeating a stated
   rule with a new input, and a parenthetical rationale. `case-21 -> FR-CART-02` and
   `case-30 -> FR-ORD-02` were relabeled to fail; `case-14 -> FR-PRD-04` was relabeled and then
   returned to pass when the PRD v0.4 alignment made the assertion grounded.
5. **Re-measure.** Next comparison uses the 2026-11-03 floor (recall 0.05, specificity 0.04, 6 to 8
   disagreements) until a fresh baseline replaces it. Then re-run the designer on the updated PRD
   (FR-CART-01 AC3, the merged FR-PRD-04) and label that run; that is the only way to see the PRD
   fix itself.
6. **Phoenix annotations (closed 2026-11-03).** The committed dataset is now the judge's source of
   truth, so Phoenix replacement is not required. Phoenix keeps the original values and stays the
   labeling UI for new runs; do not rebuild `judge/data/` from it.
7. **Confirm before spending.** Do not start a judge run without agreeing the model, the number of
   runs, and the call budget with the operator first. A three-run measurement is 150 calls.

## Comments

Renumbered from the old ticket 02 on 2026-10-29. Now depends on the human labels exported by
ticket 02.

2026-10-29: ticket 02 labels are complete for the automationexercise run (54/54 claims, three
HUMAN configs). Evidence and next steps above are based on that run's `report.md`.
