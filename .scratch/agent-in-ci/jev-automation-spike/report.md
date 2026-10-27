# Jev automation-review spike — results

Date: 2026-10-25
Model: `jev-1.13.0`
Bands: pass `>= 0.8`, fail `< 0.5` (the review layer's `DEFAULT_BANDS`)
Runs: 3 per variant
Raw data: `raw.json` (v1), `raw-v2.json` (v2)

## Input

- Case: `test-case/test-case-register-login-smoke.md`, `## Case 1` (copy in `case.md`).
- Good test and three bad variants under `variants/`.
- Support code under `support/`: the real `BasePage` and `Header`, plus a spike-only `LoginPage`
  and its fixture. The support code is part of the subject because `open()` / `expect_loaded()`
  hide actions the test itself does not show.
- Subject: `{"case": ..., "test": ..., "support": {path: source}}`.

## Question sets

- v1: `questions.py`
- v2: `questions_v2.py`, refined after v1 (the good test false-flagged on expected results and
  preconditions; the wording was too strict).
- Both use the same four questions: `steps_in_order`, `expected_results_asserted`,
  `no_invented_behavior`, `preconditions_setup`.

## Results

### v1 (means of 3 runs; full runs in `raw.json`)

| variant | steps_in_order | expected_results | no_invented | preconditions |
| --- | --- | --- | --- | --- |
| good | 0.87 | 0.73 | 0.84 | 0.48 |
| skip (only block check missing) | 0.78 | 0.21 | 0.86 | 0.56 |
| substitute (Login instead of Signup) | 0.04 | 0.29 | 0.09 | 0.51 |
| wrong_expected (URL only) | 0.74 | 0.07 | 0.50 | 0.45 |

**Kill criteria: FAIL** — the good test's `expected_results_asserted` (0.69–0.78) and
`preconditions_setup` (0.45–0.50) did not reach 0.8.

### v2 (means of 3 runs; full runs in `raw-v2.json`)

| variant | steps_in_order | expected_results | no_invented | preconditions |
| --- | --- | --- | --- | --- |
| good | 0.86 | 0.91 | 0.90 | 0.97 |
| skip (actions only, no expected assertions) | 0.60 | 0.07 | 0.72 | 0.97 |
| substitute (Login instead of Signup) | 0.04 | 0.59 | 0.08 | 0.96 |
| wrong_expected (URL only) | 0.75 | 0.09 | 0.64 | 0.97 |

**Kill criteria: PASS**

- Good: every question `>= 0.86` in all 3 runs.
- Skip: `expected_results_asserted` `0.07–0.08` in all 3 runs.
- Substitute: `steps_in_order` `0.04` in all 3 runs (and `no_invented_behavior` `0.08`).
- Wrong expected: `expected_results_asserted` `0.09–0.10` in all 3 runs.
- No missing answers; no `BLOCKED`.

## Findings

1. **The two primary questions separate strongly.** `steps_in_order` caught the wrong control
   (0.04), and `expected_results_asserted` caught both missing and weak assertions (0.07–0.10).
   The gap is wide enough that the 0.8 / 0.5 bands are plausible.
2. **Wording is decisive.** v1 false-flagged the good test on expected results and preconditions.
   v2 explicitly accepts a page-unique heading and a timestamped email, and the good test moved to
   0.86–0.97. The question text, not the test, was the problem.
3. **A subtle skip is not caught consistently.** The original "skip only the block check" variant
   was caught by v1 (0.21) but not v2 (0.70) because `LoginPage.expect_loaded()` already asserts
   the signup block. That is a real lesson: page-object readiness checks can cover a case expected
   result. The final skip variant drops all expected-result assertions, and v2 catches it (0.07).
   Production review must include the page-object source, or it will misjudge coverage.
4. **`preconditions_setup` did not discriminate in this set.** All variants scored 0.96–0.97; every
   test uses `open()` and a timestamped email. Keep it as an advisory sanity check or drop it; it
   carries no signal for the gate here.
5. **`no_invented_behavior` is redundant with `steps_in_order` for the wrong-flow variant** (both
   near 0.08), but it could catch other inventions. Keep it as a secondary/advisory question.
6. **Three runs were stable.** No answer was missing, and the runs stayed within a few points. This
   is directional, not statistical confidence.
7. **Cost:** v1 = 12 calls / 24,663 input / 984 output tokens; v2 = 12 calls / 24,852 input / 984
   output tokens.

## Recommendation

**Proceed to Stage A/B, with the v2 question set as the starting point**, and adjust:

- Gate on `steps_in_order` + `expected_results_asserted` (the strong signals).
- Keep `no_invented_behavior` as secondary/advisory until it is calibrated on real outputs.
- Drop `preconditions_setup` or keep it advisory; it did not separate anything here.
- Keep the 0.8 / 0.5 bands for now, but calibrate them on real agent-generated tests before Stage C.
- Do not make it blocking until a real agent output (not just synthetic variants) is in the fixture
  set; the page-object coverage lesson above shows synthetic tests can hide the real failure modes.

## Files

- `case.md`, `variants/`, `support/`
- `questions.py`, `questions_v2.py`
- `run.py`
- `raw.json`, `raw-v2.json`
- this report
