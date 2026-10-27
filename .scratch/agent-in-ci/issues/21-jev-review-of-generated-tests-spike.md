# 21: Spike — can Jev judge whether a generated test follows the case design?

**Type:** spike / research. The result decides whether to build the production review (Stages A–C); it
does not add production code or a gate.

**What to build:** A throwaway spike that asks TypeSafe Jev whether a generated Playwright test
follows the case's steps and expected results. Prepare one good test and three bad variants, run the
same typed question set against each, and write a report with the probabilities and a proceed/stop
recommendation.

**Why:** The deterministic quality gate checks shape (case marker, assertions, direct selectors,
file location/imports). It cannot see whether the test executes the case's steps in order, asserts
each expected result, avoids substituting a step, or sets up the preconditions. That semantic gap is
exactly what the page-object skill's rule 19 protects, and it is where generated tests rot while
staying green.

**Inputs:**

- Case: `test-case/test-case-register-login-smoke.md`, `## Case 1` (three steps; one page).
- Support code (spike-only fixtures, not `pages/`): a minimal `LoginPage`, plus the real
  `pages/base_page.py` and `components/header.py` excerpts so Jev can see what `open()`/actions do.
- One good test and three bad variants:
  - **good**: opens `/login`, checks the `New User Signup!` block, enters name/email, checks the
    values, clicks `Signup`, asserts the `Enter Account Information` page.
  - **skip**: performs the actions but drops the expected-result assertions (the entered values and
    the account-information page). The first pass dropped only the block check, but
    `LoginPage.expect_loaded()` already asserted it; the page-object source is therefore part of the
    subject.
  - **substitute**: replaces the step-1 navigate with a direct `page.goto(...)`, bypassing the page
    object (the rule-19 violation).
  - **wrong expected**: asserts a weaker/wrong outcome (e.g. the URL only, or a message from another
    flow) instead of the `Enter Account Information` page.

**Subject shape (spike script, not production):**

```json
{
  "case": "<the exact ## Case 1 section>",
  "test": "<the test file source>",
  "support": {"pages/login_page.py": "...", "pages/base_page.py": "...", "components/header.py": "..."}
}
```

**Draft questions (Noul; refine before running):**

1. `steps_in_order` — Does the test execute the case's steps in the same order, with no step skipped
   or replaced?
   - true: every case action appears in order, directly or via a page-object method that performs it.
   - false: a step is missing, reordered, or replaced by a non-equivalent shortcut.
2. `expected_results_asserted` — Does the test assert every expected result?
   - true: each expected result has an assertion that would fail if the result were absent.
   - false: one expected result is missing or replaced by a weaker check (e.g. only the URL).
3. `no_invented_behavior` — Does the test avoid actions or assertions the case does not describe?
   - true: only the case's behavior plus setup/cleanup.
   - false: it invents behavior or asserts unrelated things.
4. `preconditions_setup` — Does the test establish the case preconditions?
   - true: each precondition is met by a fixture or an explicit setup step.
   - false: a precondition is assumed or missing.

**Method:**

- Put the spike under `.scratch/agent-in-ci/jev-automation-spike/`: `case.md`, `variants/*.py`,
  `support/*.py`, `questions.py`, `run.py`, `report.md`.
- Use `typesafe_sdk` / `AsyncTypeSafeClient`, model `jev-1.13.0`, the same call shape as
  `web_test/planning/review/jev.py` (`system_one(subject.model_dump(), questions, model=...)`).
- Run each variant **3 times** to see whether the answers are stable.
- Save the raw responses as JSON next to the report.
- Do not put the spike under `web_test/` or `tests/`; it must not be collected by pytest.

**Pre-registered kill criteria (do not loosen after seeing the result):**

- Good variant: every question `>= 0.8` in at least 2 of 3 runs.
- Each bad variant: the intended question `< 0.5` in at least 2 of 3 runs.
- All three bad variants caught; at least one caught per intended question.
- No `BLOCKED` (no answer) on any intended question.
- If the criteria fail, stop: do not build the production review; report what the questions missed.

**Deliverable — `report.md`:**

- The exact case and variant sources.
- The final question set and criteria.
- A probability table per variant × question × run.
- False positives/negatives and stability notes.
- A recommendation: **proceed to Stage A** (shared Jev client + advisory integration), **change the
  questions**, or **stop**.
- Number of Jev calls and the model id.

**Out of scope:**

- Production `web_test/automation/design_review.py`, a shared `web_test.jev` client, gate statuses,
  evidence/PR-body integration, or a blocking policy.
- Calibrating on real agent runs at scale (that is Stage C).
- Changing the existing test-case review (`planning.review`) or its questions.

## Follow-up stages (open only if the spike passes)

Do not open implementation tickets before the spike's kill criteria pass. Stage A is a prerequisite
for B and C; the advisory Stage B must be validated on a real agent output before Stage C enforces.

### Stage A — Shared Jev client

- Extract `JEV_MODEL`, `JevAnswer`, a generic request/`SystemOne`, and `typesafe_system_one` into
  `web_test/jev/` (or `web_test/jev.py`).
- `planning.review.jev` imports it; `automation.design_review` will import it too.
- `web_test.jev` is a shared leaf: update ADR-0009 and the import contracts so automation may
  import it.
- Exit: existing review tests and `lint-imports` pass; no behavior change.

### Stage B — Advisory design review

- `web_test/automation/design_review.py`: `AutomationSubject` (case + generated test + changed
  page objects), `design_questions`, `review_design(system_one=...)`.
- Start from the v2 question set; include the page-object source; gate on `steps_in_order` +
  `expected_results_asserted`; keep `no_invented_behavior` advisory and drop or keep
  `preconditions_setup` advisory.
- Run after a green suite and before publish; add `AutomationEvidence.review` and a
  `## Design review` section to the summary and PR body; no blocking.
- Bound the subject; skip with a note when it is too large.
- Validate on one real agent output before Stage C.
- Exit: fake-`SystemOne` tests; advisory output only.

### Stage C — Calibrate and enforce

- Build golden fixtures from real agent runs (good/bad), not just the synthetic variants.
- Add a real agent output to the fixture set: the synthetic skip showed that a page-object
  readiness check can cover a case expected result.
- Decide bands, `NEEDS_REVIEW` behavior, and missing `TYPESAFE_API_KEY` behavior.
- Add `AutomationStatus.REVIEW_RED` (exit 1, no PR) only if the larger eval passes.
- Exit: eval kill criteria on the larger set; docs; blocking enabled.

**Secrets:** `TYPESAFE_API_KEY` comes from the environment. Never commit the key or paste it into the
report or fixtures.

**Blocked by:** None.

**Status:** ready-for-human (done; spike complete)

**Priority:** research — the report gates Stages A–C; do not integrate before the kill criteria pass.

- [x] Pick the case and record its exact text
- [x] Write the good test and the three bad variants + support files
- [x] Finalize 4–6 Noul questions with true/false criteria
- [x] Run each variant 3 times with `jev-1.13.0` and save the raw responses
- [x] Check the kill criteria and write `report.md` with a proceed/stop recommendation
- [x] No production code, pytest collection, or secrets committed

## Comments

**2026-10-25 — spike complete.**

- v1 (`questions.py`) failed the kill criteria: the good test's `expected_results_asserted` was
  0.69–0.78 and `preconditions_setup` 0.45–0.50, both below 0.8.
- v2 (`questions_v2.py`) passed: good 0.86–0.97; skip `expected_results_asserted` 0.07–0.08;
  substitute `steps_in_order` 0.04; wrong expected `expected_results_asserted` 0.09–0.10; no
  missing answers.
- The skip variant changed between runs: the first version dropped only the block check, but
  `LoginPage.expect_loaded()` already asserted it. v2 drops all expected-result assertions. This is
  why the page-object source must be in the subject.
- Recommendation: proceed to Stage A/B with the v2 question set; gate on `steps_in_order` +
  `expected_results_asserted`; keep `no_invented_behavior` advisory and drop or keep
  `preconditions_setup` advisory; calibrate on a real agent output before Stage C.
- Report: `.scratch/agent-in-ci/jev-automation-spike/report.md`.
