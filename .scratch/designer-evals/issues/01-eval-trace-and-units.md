# 01: Build the designer eval trace and requirement/case units

**What to build:** Run `design_test_cases` once for one PRD, save the run artifacts, and attach
one `EVALUATOR` span per PRD requirement and one per generated case under the designer agent
span in Phoenix. Write the code annotations needed to review the run. The result is a trace a
human can open and annotate; it is not the coverage report yet.

**Blocked by:** None.

**Status:** ready-for-agent

**Shape:**
- Types: `EvalUnit` (kind, target_id, span_id, attributes), `EvalRun` (run_id, prd, model,
  usage, design, units). `DesignOutput` stays the existing Pydantic model; run/unit records
  written to JSON are Pydantic, in-memory eval types are dataclasses.
- Boundary: Phoenix project `web-test-designer-eval`; files under
  `.scratch/designer-evals/runs/<run_id>/`.
- Invariants: every PRD requirement has exactly one requirement span; every generated case
  has exactly one case span; eval spans share the designer trace and have the agent span as
  parent; code annotations are `CODE`; no production module changes.

## Tasks

- [x] Pin the PRD set and `WEB_TEST_DESIGN_MODEL`; record the model in `run.json`.
- [ ] Record usage; `design_test_cases` currently returns only `DesignOutput`.
- [x] Parse requirements from `### FR-*` headings, stopping at the next `##` or `###` heading.
- [x] Run the designer; save `design.json`, `run.json`, and rendered markdown.
- [x] Fetch the designer agent span and create late-child `EVALUATOR` spans:
      one per requirement, one per case.
- [x] Put the requirement text, claimed cases, case JSON, claimed requirements, `run_id`, and
      PRD name on the spans.
- [ ] Write `CODE` annotations: `requirement_claimed`, `case_requirement_ids`,
      `case_duplicate`.
- [x] Save `units.json` mapping `span_id` to requirement/case.
- [x] Add tests for requirement parsing and unit mapping.
- [x] Verify the trace structure in Phoenix (REST); 6 requirement + 7 case spans under the agent.
- [x] Run `uv run pytest`, `uv run basedpyright`, `uv run lint-imports`,
      `uv run ruff check --select F401`.

## Out of scope

- Human label export and coverage report (ticket 02).
- Semantic judge (ticket 03).
- Phoenix experiments (ticket 04).
- CI or gate changes.
- Changing the designer prompt/model.

## Risks

- Phoenix annotation UI is span-centric; the eval-unit shape must stay readable.
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
  ├─ EVALUATOR requirement FR-*
  ├─ EVALUATOR requirement FR-*
  ├─ EVALUATOR case 1
  └─ EVALUATOR case N
  │
  ▼
units.json
```

## Comments

Created 2026-10-29 from `.scratch/designer-evals/spec.md`. Replaces the code-only half of the
old coverage ticket; the report moves to ticket 02.

2026-10-29: parser + eval units implemented in `.scratch/designer-evals/run_eval.py`.
Run `register-login-20261029T060452Z` produced 6 requirement + 7 case `EVALUATOR` spans in
project `web-test-designer-eval`. Artifacts are under
`.scratch/designer-evals/runs/register-login-20261029T060452Z/`. Code annotations and usage
capture remain.
