# 18: Add AC alignment, step quality, and observability checks to the Jev review

**What to build:** Extend the advisory Jev review of the designer's output with three checks:

1. **AC alignment** — is each case supported by the PRD requirement text and acceptance criteria?
2. **Step quality** — is each step reasonable, complete, and does it include the required actions/inputs?
3. **Expected result observability** — is each expected result specific and observable in the PRD text?

The review stays advisory. It does not block the plan PR, edit the designer's output, or add images.

**Blocked by:** none. Extends the reviewer seam introduced in ticket 17.

**Category:** enhancement

**Status:** ready-for-agent

## Decisions from the 2026-10-20 experiment

- Replace `grounded_{i}` with `ac_{i}`. The two questions were nearly duplicate; the AC question is the validated one.
- Do **not** add `step_{i}_{j}_reachable`. In v2 it did not catch the skipped-data case (0.80); v3's `complete` question caught it (0.12).
- Pin `JEV_MODEL = "jev-1.13.0"`. The experiment used that model; `jev-latest` is not reproducible.
- Merge the step-level checks into one **Step quality** report section. Keep AC alignment separate.
- Use only `prd_text + cases`. No `screen_descriptions`, no Appendix A dependency, no images.

## Question set

For each case with 1-based index `i`:

- `ac_{i}` — AC alignment.

For each step with 1-based index `j`:

- `step_{i}_{j}_reasonable` — does the step name a concrete action and target that exists in the PRD text and is consistent with the flow?
- `step_{i}_{j}_complete` — does the step include every action required to produce its expected result, including required data entry?
- `step_{i}_{j}_observable` — is the expected result a specific, observable outcome in the PRD text or its verbatim messages?

Use the exact `Noul` instructions and `criteria` validated in `.scratch/jev-register-login-phase1/artifacts/request-v3.json` and `artifacts/request-v4c.json`.

## Implementation

- Add `ReviewStep(index, action, expected_result)` as a Pydantic model.
- Change `ReviewCase.steps` from `list[str]` to `list[ReviewStep]`.
- Replace `_questions()` groundedness generation with the four question groups above.
- Keep `ReviewState` as `prd` + `cases`.
- Pin `JEV_MODEL` to `jev-1.13.0`.
- Keep the `system_one` seam, `_normalize`, and `run_review` advisory behavior unchanged.

## Report

`render_report()` should emit:

```text
## Jev review (advisory)

**AC alignment:** X/Y cases aligned

**Step quality:** X/Y reasonable, Y/Z complete, Z/W observable

**Findings**

- Case 3: <scenario> (AC alignment, p=...)
- Case 3, step 2: <action> (completeness, p=...)
- Case 4, step 1: <action> (observability, p=...)

**Needs review (confidence < 0.8)**

- ...

_Advisory: Jev does not block; a human decides._
```

- Step findings must name the sub-check: reasonable, complete, or observable.
- Normalize step action to one line and clip long labels.
- Ignore unknown question IDs.
- Skip missing verdicts rather than raising.

## Acceptance criteria

- [x] `build_request()` produces `ac_{i}` and the three `step_{i}_{j}_*` groups; no `grounded_` or `reachable`.
- [x] `ReviewCase.steps` preserves `action`, `expected_result`, and `index`.
- [x] `render_report()` shows AC alignment and a merged Step quality section with three counts.
- [x] Findings name the case, step, and failing sub-check.
- [x] Low-confidence items still appear under `Needs review`.
- [x] `run_review()` still returns `None` on Jev failure; `plan` still proceeds without a review.
- [x] `uv run pytest tests/planning` passes.
- [x] `uv run pytest` passes.
- [x] One live review-only run on a real PRD produces the new report without opening a PR.

## Tests

Update `tests/planning/test_review.py`:

- Question IDs for a 1-case, 2-step design: `ac_1`, `step_1_1_reasonable`, `step_1_1_complete`, `step_1_1_observable`, and the same for step 2.
- `request.state.cases[0].steps[0]` is a `ReviewStep` with the original action and expected result.
- No `grounded_` or `reachable` keys.

Update `tests/planning/test_review_report.py`:

- AC alignment counts and findings.
- Merged Step quality counts.
- Findings include the failing sub-check name.
- Low-confidence items for new checks.
- Unknown IDs are ignored.

Update `tests/planning/test_plan.py` if the report section names change.

## Out of scope

- Defining or enforcing PRD completeness.
- Screenshots, vision models, `screen_descriptions`, or Appendix A parsing.
- Coverage, deduplication, `requirement_ids` existence, or case-body schema checks.
- Blocking the plan PR or replacing the human Gate.
- Changing the designer or its prompts.
- Batching or splitting requests for very large artifacts.

## Evidence

- `.scratch/jev-register-login-phase1/RESULTS-v3.md` — `complete` catches the skipped-step case; `reachable` does not.
- `.scratch/jev-register-login-phase1/RESULTS-v4b.md` — removing `screen_descriptions` did not change the verdicts.
- `.scratch/jev-register-login-phase1/RESULTS-v4c.md` — removing Appendix A did not change the verdicts.
- `.scratch/jev-register-login-phase1/RESULTS-login-smoke.md` — cases must stay within the PRD evidence scope; Jev flags over-specified cases.
- `.scratch/prd-to-tests/issues/17-jev-review-of-designer-output.md` — the original review experiment and design.

## Comments

**2026-10-20 — implemented.**

- `web_test/planning/review.py`: added `ReviewStep`, kept steps structured, replaced `grounded_{i}` with `ac_{i}`, added `reasonable` / `complete` / `observable` per step, pinned `JEV_MODEL = "jev-1.13.0"`.
- `web_test/planning/review_report.py`: replaced groundedness with AC alignment and a merged Step quality section with three counts; findings name the sub-check.
- Tests updated in `tests/planning/test_review.py`, `test_review_report.py`, and `test_plan.py`.
- `uv run pytest tests/planning`: 34 passed.
- `uv run pytest`: 103 passed, 1 skipped.
- Live review-only run on `prd/login-smoke.md` (no PR opened): 3 cases, 8 steps; AC alignment 3/3; step quality 8/8 reasonable, 8/8 complete, 7/8 observable; one finding, five low-confidence items.

The run still uses `prd_text + cases` only. No images, screen descriptions, or Appendix A parsing were added.
