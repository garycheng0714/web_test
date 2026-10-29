# 01: Evaluate designer requirement coverage

**What to build:** A rerunnable, report-only eval that runs `design_test_cases` on a pinned
set of PRDs and reports requirement coverage and traceability. For each PRD it must show the
PRD requirement IDs, the IDs claimed by generated cases, the IDs a human labels as actually
covered, missing requirements, invented IDs, cases with empty `requirement_ids`, duplicate
cases, and the coverage rate with a Wilson 95% CI. Save each run's `DesignOutput` JSON,
rendered test-case markdown, model id, and usage. No gate change.

**Blocked by:** None.

**Status:** needs-triage

**Shape:**
- Types: `DesignerEvalRun` (PRD, `DesignOutput`, model, usage),
  `RequirementCoverage` (requirement_id, claimed, covered, case_ids), `CoverageReport`.
- Boundary: eval files under `.scratch/designer-evals/`; `DesignOutput` is the existing
  Pydantic model in `web_test/planning/schema.py`; eval types are dataclasses.
- Invariants: every PRD requirement is accounted for; invented IDs are reported, not
  silently accepted; `covered` comes from human labels, not `requirement_ids`; the report
  includes a CI and the sample size.

**Module plan (evaluator):**
1. Input: PRD text, `DesignOutput` JSON, human labels JSONL.
2. Output: `CoverageReport` and per-PRD JSON/JSONL artifacts.
3. External boundaries: `design_test_cases` model call; file I/O.
4. Domain types vs adapters: `RequirementCoverage`/`CoverageReport` dataclasses; adapters
   for the designer call and file storage.
5. Single-variation parts: reuse `web_test/planning/review/structure.py` checks and
   `render_document`; do not duplicate them.
6. Responsibilities: run the designer on a PRD; measure coverage/traceability; render the
   report.

## Tasks

- [ ] Pin the PRD set: `prd/register-login.md`, `prd/login-smoke.md`,
      `prd/live-evidence.md`; add `.scratch/automationexercise/prd.md` if useful.
- [ ] Pin `WEB_TEST_DESIGN_MODEL` and record it in the report.
- [ ] Run the designer on each PRD; save `DesignOutput` JSON + rendered markdown + usage.
- [ ] Extract PRD requirement IDs (`FR-*`) and compare with case `requirement_ids`.
- [ ] Add code checks: missing, invented, empty, duplicate, and structure.
- [ ] Create a human label file: per requirement `covered`/`not covered`; per case
      `tests its claimed requirement`/not.
- [ ] Report coverage rate + Wilson CI, false tags, missing IDs, per PRD.
- [ ] Add tests for the code-only evaluator with fixtures.
- [ ] Run `uv run pytest`, `uv run basedpyright`, `uv run lint-imports`,
      `uv run ruff check --select F401`.

## Out of scope

- Semantic judge (ticket 02).
- CI report or gate (ticket 03).
- Automation eval.
- Changing the designer prompt/model.

## Risks

- Only 3–4 PRDs; CIs will be wide.
- Single annotator; add delayed self-review or a second person.
- `requirement_ids` can be gamed; human labels are the ground truth.
- Model cost per run.

## Flow

```text
PRDs
  │
  ▼
design_test_cases (pinned model)
  │
  ▼
DesignOutput + rendered markdown
  │
  ▼
code checks + human labels
  │
  ▼
coverage report + Wilson CI
```

## Comments

Created 2026-10-29 from `.scratch/designer-evals/spec.md`.
