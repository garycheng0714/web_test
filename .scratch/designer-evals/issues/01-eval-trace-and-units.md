# 01: Build the designer eval trace and claim units

**What to build:** Run `design_test_cases` once for one PRD, save the run artifacts, and attach
one `EVALUATOR` claim span per (requirement, case) pair under the designer agent span in
Phoenix. Each claim span carries the requirement text and the case JSON together. Add one
requirement span for each requirement with no claim. The result is a trace a human can open and
annotate; it is not the coverage report yet.

**Blocked by:** None.

**Status:** ready-for-agent

**Shape:**
- Types: `EvalUnit` (kind `claim`/`requirement`, target_id, span_id, attributes), `EvalRun`
  (run_id, prd, model, usage, design, units). `DesignOutput` stays the existing Pydantic
  model; run/unit records written to JSON are Pydantic, in-memory eval types are dataclasses.
- Boundary: Phoenix project `web-test-designer-eval`; files under
  `.scratch/designer-evals/runs/<run_id>/`.
- Invariants: every claimed (requirement, case) pair has exactly one claim span; every
  requirement with no claim has exactly one missing-requirement span; invented IDs get claim
  spans with `claim.requirement_exists=false`; eval spans share the designer trace and have the
  agent span as parent; no production module changes.

## Tasks

- [x] Pin the PRD set and `WEB_TEST_DESIGN_MODEL`; record the model in `run.json`.
- [x] Add the pinned `eval` dependency group for Phoenix client/instrumentation.
- [ ] Record usage; `design_test_cases` currently returns only `DesignOutput`.
- [x] Parse requirements from `### FR-*` headings, stopping at the next `##` or `###` heading.
- [x] Run the designer; save `design.json`, `run.json`, and rendered markdown.
- [x] Fetch the designer agent span and create late-child `EVALUATOR` claim spans:
      one per (requirement, case) pair, plus one missing-requirement span.
- [x] Put the requirement text, case JSON, requirement/case IDs, `run_id`, and PRD name on
      the claim spans.
- [ ] Write `CODE` annotations: `requirement_exists`, `case_duplicate`.
- [x] Save `units.json` mapping `span_id` to claim or missing requirement.
- [x] Add tests for requirement parsing and unit mapping.
- [x] Verify the trace structure in Phoenix (REST); 7 claim spans under the agent for the
      register-login run.
- [x] Run `uv run pytest`, `uv run basedpyright`, `uv run lint-imports`,
      `uv run ruff check --select F401`.

## Out of scope

- Human label export and coverage report (ticket 02).
- Semantic judge (ticket 03).
- Phoenix experiments (ticket 04).
- CI or gate changes.
- Changing the designer prompt/model.

## Risks

- Claim spans are the review unit; keep requirement text and case JSON together.
- Late child spans are validated, but ingestion can lag; use retries.
- Only 3–4 PRDs; do not overfit the unit schema to one PRD.

## Flow

```text
PRD
  │
  ▼
design_test_cases
  │
  ├─ design.json / run.json
  │
  ▼
agent span
  │
  ├─ EVALUATOR claim FR-ACC-01 <- case-1
  ├─ EVALUATOR claim FR-ACC-04 <- case-4
  └─ EVALUATOR requirement FR-ACC-03 (missing)
  │
  ▼
units.json
```

## Comments

Created 2026-10-29 from `.scratch/designer-evals/spec.md`. Replaces the code-only half of the
old coverage ticket; the report moves to ticket 02.

2026-10-29: parser + claim units implemented in `.scratch/designer-evals/run_eval.py`.
Claim-centric run `register-login-20261029T063052Z` produced 7 `claim` spans (11 total
spans) in project `web-test-designer-eval`. Artifacts are under
`.scratch/designer-evals/runs/register-login-20261029T063052Z/`. Code annotations and usage
capture remain.
