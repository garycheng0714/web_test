# 16: Right-size the designer's case generation

**What to build:** Stop the designer over-generating. Per requirement it should produce one happy-path
case, at most one negative/validation case, and a boundary case only when the PRD states the boundary
or the UI exposes it. Behaviour the PRD leaves undefined is returned as `open_questions`, not as a
case. Cases that merely restate others (end-to-end re-runs, message sweeps, header/role checks) are
dropped.

**Blocked by:** None.

**Category:** enhancement

**Status:** ready-for-human

- [x] The skill's coverage/boundary/dedup/output sections encode the tighter policy
- [x] The designer returns `DesignOutput(cases, open_questions)`
- [x] The rendered file ends with an optional `## Open Questions` section
- [x] The plan stage and publisher carry open questions through
- [x] Tests updated; `uv run pytest` green

## Comments

The sample PRD (`register-login.md`, 6 FRs) produced 26 cases, over half of them inferred from
behaviour the PRD leaves undefined (validation messages, case-sensitivity, session persistence,
permission redirects, email reuse, double-submit) or cross-cutting duplicates (an e2e flow, a message
sweep, a header/role check). Cases asserting guessed behaviour will fail against the real system.

Implemented:

- `.agents/libraries/test_case_designer/qa-test-case-generation/SKILL.md` — Coverage (one happy path,
  at most one negative/validation, a boundary only when stated/visible), Boundary (only when stated),
  Deduplication (no case that restates others), Output (`cases` + `open_questions`; undefined
  behaviour goes to `open_questions`, never a case).
- `web_test/planning/schema.py` — `DesignOutput(cases: list[Case], open_questions: list[str] = [])`.
  (Ticket 12 chose `list[Case]` under YAGNI — "no second field"; there is a second field now.)
- `web_test/planning/designer.py` — `output_type=DesignOutput`; returns it.
- `web_test/planning/cases_writer.py` — `render_document(..., open_questions)`, `_open_questions`
  block, `CaseWriter.write(prd_stem, cases, open_questions)`.
- `web_test/planning/publisher.py` — `publish(..., open_questions)`; the PR body lists them.
- `web_test/planning/entrypoint.py` — reads `design.cases` / `design.open_questions`.
- `.scratch/prd-to-tests/spec.md` — designer + artifact sections updated.

Effect: the sample PRD went **26 → 12 cases (+14 open questions)**.

`uv run pytest`: 86 passed, 1 skipped.
