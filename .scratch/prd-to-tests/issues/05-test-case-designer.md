# 05: Test Case designer and test-case artifact

**What to build:** A single Pydantic AI agent that reads a PRD (markdown/plain text), loads the
`qa-test-case-generation` skill through Pydantic AI Harness `Skills`, and produces the test-case
document. The document is the qa table format, rendered from a structured result and carrying an
`approval` state.

**Blocked by:** 01

**Status:** ready-for-human

- [x] A single agent turns PRD text into a structured `QaReport` (no separate PRD parsing step)
- [x] The `qa-test-case-generation` skill is loaded on demand via harness `Skills` (deferred capability)
- [x] Each case records: id, `requirement_ids`, module/feature, scenario, preconditions, steps, test data, expected result, priority, severity, test type, status, notes
- [x] `priority`, `severity`, `test_type`, `status` use constrained (enum) values
- [x] Duplicate scenarios are merged per the skill's deduplication rules
- [x] The document is rendered to the qa table markdown under `.scratch/automationexercise/test-cases.md`
- [x] The document starts in the unapproved state (`approval: draft`) via front-matter
- [x] Agent-level tests override the model and assert the produced document

## Comments

Implemented as a single agent (ADR-0005):

- `web_test/schema.py` — `Priority`, `Severity`, `CaseType`, `CaseStatus` enums; `Case` and
  `QaReport` models.
- `web_test/qa_designer.py` — the designer agent and `design_test_cases(prd_text, *, model=None)`.
  The agent runs with `output_type=QaReport` and
  `capabilities=[Skills(.agents/libraries/test_case_designer,
  include=['qa-test-case-generation'], workspace=LocalWorkspaceBackend(REPO_ROOT))]`; its
  instructions tell the model to `load_capability('qa-test-case-generation')` first.
- `web_test/paths.py` — repo/feature paths (`PRD_PATH`, `TEST_CASES_PATH`).
- `.agents/libraries/test_case_designer/qa-test-case-generation/SKILL.md` — a **house variant**:
  the coverage / boundary / deduplication rules from the original `references/` are inlined
  (harness `Skills` only loads `SKILL.md`) and the output section is rewritten for structured
  output. Adapted from `saleem-daqa/qa-test-case-generation` (MIT).
- `web_test/document.py` — `render(report)` produces the qa table markdown with `approval: draft`
  front-matter; `write_report()` refuses to overwrite an approved file unless `force=True`.
- Tests: `tests/test_qa_designer.py` (model overridden with `TestModel(custom_output_args=...)`;
  structured result; enum validation) and `tests/test_document.py` (render + `is_approved`).
  No network.

`base_url` was dropped (no PRD model); the automation stage will need it from elsewhere (e.g. a CLI
argument). The qa mockup/live-URL sections are out of v1 scope.

`uv run pytest`: 12 passed, 1 failed — only the pre-existing header PUA test.

**Artifact shape superseded (ADR-0006).** The designer agent and `QaReport` stand, but the
artifact it feeds changed: cases are now one `test-case/<id>.md` per case with a front-matter, opened
as a PR — not a single qa-table document at `.scratch/<feature>/test-cases.md` with `approval`. The
`render` / `is_approved` path is replaced by the ticket-06 rewrite.
