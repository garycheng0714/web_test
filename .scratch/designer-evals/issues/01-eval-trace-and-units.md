# 01: Build the designer eval trace and claim units

**What to build:** Run `design_test_cases` once for one PRD, save the run artifacts, and attach
one `EVALUATOR` requirement span per PRD requirement under the designer agent span, and one
claim span per (case, valid requirement) pair under that requirement span. Each claim span
carries the requirement text and the case rendered as markdown (`input.mime_type` and
`output.mime_type` are `text/markdown`). The result is a trace a human can open and annotate; it
is not the coverage report yet.

**Blocked by:** None.

**Status:** ready-for-human

**Shape:**
- Types: `EvalUnit` (kind `claim`/`requirement`, target_id, span_id, attributes), `EvalRun`
  (run_id, prd, model, usage, design, units). `DesignOutput` stays the existing Pydantic
  model; run/unit records written to JSON are Pydantic, in-memory eval types are dataclasses.
- Boundary: Phoenix project `web-test-designer-eval`; files under
  `evals/designer/runs/<run_id>/`.
- Invariants: every PRD requirement has exactly one requirement span; every case × valid FR has
  exactly one claim span; `FR-*-ACn` normalizes to the parent; `MSG-*`／`ROLE-*` and unknown
  `FR-*` do not create claims; multi-FR cases are flagged; eval spans share the designer trace;
  no production module changes.

## Tasks

- [x] Pin the PRD set and `WEB_TEST_DESIGN_MODEL`; record the model in `run.json`.
- [x] Add the pinned `eval` dependency group for Phoenix client/instrumentation.
- [x] Record usage by summing the trace's LLM spans into `run.json`.
- [x] Parse requirements from `### FR-*` headings, stopping at the next `##` or `###` heading.
- [x] Normalize `FR-*-ACn` to the parent `FR-*`; keep `MSG-*`／`ROLE-*` as invented.
- [x] Run the designer; save `design.json`, `run.json`, and rendered markdown.
- [x] Fetch the designer agent span and create late-child `EVALUATOR` claim spans:
      one per (requirement, case) pair, plus one missing-requirement span.
- [x] Put the requirement text, the rendered case, requirement/case IDs, `run_id`, and PRD name on
      the claim spans.
- [x] Write `CODE` annotation `case_duplicate`; non-requirement and invalid IDs go to report.
- [x] Save `units.json` mapping `span_id` to claim or missing requirement.
- [x] Add tests for requirement parsing, unit mapping, duplicates, and usage.
- [x] Verify the trace structure in Phoenix (REST); 7 claim spans under the agent for the
      register-login run.
- [x] Add case IDs from `case-{index}-{test_type}` and drop non-requirement IDs.
- [x] Run `uv run pytest`, `uv run basedpyright`, `uv run lint-imports`,
      `uv run ruff check --select F401`.

## Out of scope

- Human label export and coverage report (ticket 02).
- Semantic judge (ticket 03).
- Phoenix experiments (ticket 04).
- CI or gate changes.
- Changing the designer prompt/model.

## Risks

- Claim spans are the review unit; keep requirement text and the rendered case together.
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
  ├─ EVALUATOR requirement FR-ACC-04
  │    ├─ EVALUATOR claim case-1-ui -> FR-ACC-04
  │    └─ EVALUATOR claim case-2-functional -> FR-ACC-04
  └─ EVALUATOR requirement FR-ACC-03 (missing)
  │
  ▼
units.json
```

## Comments

Created 2026-10-29 from `evals/designer/spec.md`. Replaces the code-only half of the
old coverage ticket; the report moves to ticket 02.

2026-10-29: parser + claim units implemented in `evals/designer/run_eval.py`.
Claim-centric run `register-login-20261029T070829Z` produced 7 `claim` spans, 14 CODE
annotations, and usage `{prompt: 8992, completion: 6023, total: 15015, cache_read: 3840}`
in project `web-test-designer-eval`. Artifacts are under
`evals/designer/runs/register-login-20261029T070829Z/`.

2026-10-29: ID policy option 2 implemented: `FR-*-ACn` normalizes to the parent `FR-*`;
`MSG-*` / `ROLE-*` and unknown `FR-*` are dropped to diagnostics, not claims. House
login-smoke run `login-smoke-20261029T083652Z` produced 3 normalized claims.

2026-10-29: hierarchical units implemented. `requirement FR-*` spans now parent the claim
spans; case IDs use `case-{index}-{test_type}` (DataPersistence -> `data-persistence`);
non-requirement labels are dropped to `run.json` diagnostics. House login-smoke run
`login-smoke-20261029T114901Z` produced 1 requirement + 2 claims. Old-skill trace
`512dc3885250e902afbcc7a4fb498d04` produced 1 requirement + 7 claims, with 8
non-requirement labels reported.
