# 29: Separate teardown from test steps

**What to build:** Give `Case` an explicit teardown, mirroring `preconditions`, so the designer
stops putting test-data cleanup into `steps`. A registration case currently ends with "delete the
account created in this test"; the designer eval reads that as an assertion about `FR-ACC-06`
inside a case that claims `FR-ACC-01`/`FR-ACC-02`, so good hygiene looks like an alignment defect.

**Blocked by:** None.

**Status:** ready-for-agent

**Shape:**
- Types: `Case.teardown: list[str] = []` (boundary, Pydantic) and
  `ReviewCase.teardown: list[str] = []`. String items mirror `preconditions`; `list[Step]` is
  rejected because an `expected_result` would make cleanup look like verification again.
  `postconditions` is rejected because it names end state, not the reset actions.
- Boundary: `design.json` and the rendered `test-case.md` gain an optional `### Teardown` section;
  Phoenix claim spans render it through `render_case_section`.
- Invariants: teardown never counts as a verification assertion for the designer eval; a case with
  an empty teardown renders exactly as today; a file without `### Teardown` still parses.

## Tasks

- [ ] `web_test/planning/schema.py`: add `Case.teardown: list[str] = []`.
- [ ] `web_test/planning/cases_writer.py`: render `### Teardown` as a bullet list after the steps
      and before Notes; omit the section when empty.
- [ ] `web_test/planning/review/subject.py`: add `ReviewCase.teardown`;
      `web_test/planning/review/service.py` maps it from `Case`.
- [ ] `web_test/planning/review/parser.py`: parse `### Teardown`, tolerating its absence.
- [ ] House skill `.agents/libraries/test_case_designer/qa-test-case-generation/SKILL.md`: add
      `teardown` to Output, with the rule that test-data cleanup goes there and never in `steps`.
- [ ] `web_test/planning/review/questions.py`: confirm the AC-alignment questions do not treat
      teardown as a verification step; bump `question_set_version` if the question set changes.
- [ ] `.scratch/designer-evals`: remove any teardown exception from the grounding rule. A cleanup
      step left in `steps` is a `wrong_assertion_to_requirement` finding, not something to ignore.
- [ ] Tests: schema default, renderer with and without teardown, parser round-trip, review mapping,
      and an eval claim span that shows teardown but does not count it.
- [ ] Update `tests/fixtures/golden/case_document_register_login.md`; the golden case document
      gains a `### Teardown` section when a case has one.
- [ ] Run `uv run pytest`, `basedpyright`, `lint-imports`, `ruff check --select F401`.

## Out of scope

- Executing teardown in the automation stage. The automator reads the section; there is no
  enforcement.
- Changing the vendored old skill (`.agents/skills/qa-test-case-generation/`).
- Checking teardown quality (safe, idempotent, only touches data the case created).

## Risks

- The rendered format changes; every consumer of `test-case.md` must tolerate a missing section.
  Today that is `review/parser.py` and `automation/case_file.py` (front matter only).
- Old `design.json` files have no `teardown`; the Pydantic default keeps them valid.
- Designers can still put cleanup in `steps`. The eval will flag it as
  `wrong_assertion_to_requirement`, which is the signal we want, not a regression.
- If the designer eval uses a temporary teardown carve-out before this ships, it must be removed
  here.

## Comments

Opened 2026-10-29 from the designer eval on `.scratch/automationexercise/prd.md`.

Evidence: in run `house-automationexercise-20261029`, `case-1-functional` ends with "Delete the
account created in this test ... `ACCOUNT DELETED!` is displayed and the session is no longer logged
in (test data is not left behind)". The old skill did not add cleanup steps, so labeling this as a
failure would confuse the old-skill vs house-skill comparison instead of measuring assertion
discipline. Hence the fix belongs in the schema and the skill, not in the eval's label rules.

Related: 12 (per-case test-case format), 16 (right-size the designer), 22a (structure checks), 23
(review an existing test-case file).
