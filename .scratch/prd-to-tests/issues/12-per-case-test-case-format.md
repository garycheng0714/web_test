# 12: Per-case test-case file format

**What to build:** Change the Test Case designer's output and the renderer so the plan stage emits one
`test-case/test-case-<id>.md` per case — in the format of the existing sample
(`test-case/test-case-0001.md`) — instead of a single qa-table document.

**Blocked by:** None (can start immediately).

**Status:** ready-for-human

- [x] `Case.steps` is a list of `Step(action, expected_result)`; `QaReport` and its report-level fields are removed
- [x] `design_test_cases` returns `list[Case]` and the designer agent's `output_type` is `list[Case]`
- [x] `Case` keeps `requirement_ids`, `module_feature`, `test_scenario`, `preconditions`, `priority`, `severity`, `test_type`, `notes`; drops `test_case_id`, `test_data`, `status`
- [x] A pure `render_case(case, *, id, base_url) -> str` produces the file; unit-tested
- [x] File layout: hand-written front-matter template (inline `requirement_ids`, key order `id`, `base_url`, `requirement_ids`, `priority`, `test_type`), `# {module_feature}: {test_scenario}`, `**Severity:** …`, `## Preconditions`, `## Test Steps` table, `## Notes` (empty Preconditions/Notes sections omitted)
- [x] The rendered front-matter parses with `web_test/automation/case_file.py`'s `CaseFile`
- [x] The house skill `qa-test-case-generation/SKILL.md` output returns only cases, and its `clarifications_needed` wording moves to the case-level `notes`
- [x] Old `render` / `write_report` / `is_approved` / `ApprovedDocumentError` removed; `tests/planning/*` updated

## Comments

Decisions from review:

- **Steps → pairs.** The skill's old `test_steps: list[str]` + single `expected_result` becomes
  `steps: list[Step]`; the reference file already asserts per step.
- **Skill outputs only cases.** `requirement_summary`, `coverage_areas`, `assumptions`,
  `clarifications_needed`, `missing_unclear_requirements`, `suggested_improvements` are removed — no
  downstream consumer. Ambiguity/assumptions move to the case-level `notes`.
- **No model id.** The model does not emit an id; `plan` assigns `test-case-%04d` (ticket 13).
- **`severity` stays** but has no consumer today (not in front-matter, not in the planned marker
  ticket 08); it is rendered as a human-readable line. `status` and `test_data` are dropped.
- **Hand-written front-matter template**, not `yaml.safe_dump` defaults (which sort keys and emit a
  block list), to match the sample byte-for-byte. Values are enums/tokens, so no escaping risk.
- **`base_url` stays for now**; where it comes from is deferred to ticket 14.

The reference `test-case-0001.md` was a hand-written sample (see ticket 05's comment), so it is the
target shape by agreement, not because it was a spec.

Implemented:

- `web_test/planning/schema.py` — added `Step(action, expected_result)`; `Case` now
  `requirement_ids`, `module_feature`, `test_scenario`, `preconditions`, `steps`, `priority`,
  `severity`, `test_type`, `notes`; removed `QaReport` and `CaseStatus`.
- `web_test/planning/designer.py` — `design_test_cases(...) -> list[Case]`, `output_type=list[Case]`,
  reworded `INSTRUCTIONS`; dropped the unused `PRD_PATH` import.
- `web_test/planning/document.py` — replaced the qa-table `render` / `write_report` / `is_approved` /
  `ApprovedDocumentError` with `render_case(case, *, id, base_url) -> str`: hand-written front-matter
  (`id`, `base_url`, inline `requirement_ids`, `priority`, `test_type`), `# {module}: {scenario}`,
  `**Severity:** …`, `## Preconditions`, `## Test Steps` table, `## Notes`; empty Preconditions/Notes
  omitted; `|`/newlines escaped in table cells.
- Removed `web_test/planning/plan.py` (old single-doc path) and `paths.TEST_CASES_PATH`; ticket 13
  builds the new `plan` command.
- `.agents/libraries/test_case_designer/qa-test-case-generation/SKILL.md` — Output returns only the
  cases (new fields, per-step `expected_result`); `clarifications_needed` and `test_data` wording
  removed (ambiguity → the case's `notes`, representative values → the step).
- Tests: rewrote `tests/planning/test_designer.py` (list output; unknown `test_type` rejected) and
  `tests/planning/test_document.py` (`render_case` format, empty-section omission, and a
  `CaseFile.from_text` round-trip); deleted `tests/planning/test_plan.py`.

`uv run pytest`: 62 passed, 1 skipped.

Not done (out of this ticket's scope): `docs/adr/0005`, `docs/adr/0006`, and
`.scratch/prd-to-tests/spec.md` still describe `QaReport` / the old artifact; the spec rewrite is
tracked separately (see ticket 06's/AI-CI notes).
