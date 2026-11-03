# 06: Move the claim unit to acceptance criteria

**What to build:** One test case per acceptance criterion, so a claim is `(case, AC)` instead of
`(case, FR)`. The designer reads the PRD, picks one criterion per case, and the eval judges that
criterion alone. This removes the whole class of "the case asserts one step beyond its FR" disputes
by construction.

**Blocked by:** nothing to start the decision. The schema work waits on that decision.

**Status:** needs-triage

**Shape:**
- Types: `Case.ac_ids: list[str]` in `web_test/planning/schema.py`; `requirement_ids` becomes a
  derived view so the publisher, review pipeline and automation reader keep working unchanged.
  The eval already has `AcceptanceCriterion(id, index, text)` in `designer_eval/requirements.py`.
- Boundary: the rendered yaml block (`cases_writer`), the read-back in `review/parser.py` and
  `automation/case_file.py`, and the Phoenix claim span (id becomes
  `case-3-functional->FR-PRD-04-AC1`).
- Invariants: exactly one ac_id per case; every ac_id resolves to a criterion of its requirement;
  a requirement with a criterion and no case counts as uncovered; `duplicated` cannot occur because
  a case can no longer carry a second requirement.

## State when this ticket was opened

- PRD v0.5: 25 requirements and 38 criteria, each numbered by the author (`- **AC-N**: ...`).
  `parse_requirements` reads them; `tests/designer_evals/test_data_invariants.py` enforces that
  every requirement has one, that rows point at requirements the PRD defines, and that row text
  follows the PRD's current numbers.
- The automationexercise judge dataset holds 49 single-requirement claims (17 fail, 32 pass),
  aligned to v0.5 including one label change (`case-23`).
- The judge defaults to `kimi-k2.7-code` and reports `fail_recall` / `pass_specificity` with the
  confusion counts. The last measurement (`verify-kimi-run1`) predates the v0.5 label changes, so
  it is not a baseline.

## Tasks

- [ ] Decide AC-level or stay FR-level. This is the only open question.
- [ ] Add `ac_ids` to the schema, migrate the writer, both readers, and derive `requirement_ids`.
- [ ] Rewrite the designer skill's Traceability and Coverage sections: one criterion per case.
- [ ] Switch the eval units to case x AC and add the `case_spans_multiple_acs` CODE check.
- [ ] Narrow the judge input and criterion to one acceptance criterion.
- [ ] Rebuild the fixture from a designer run on the current PRD and relabel at AC level.
- [ ] Run three times for the new baseline, after confirming the budget.
- [ ] Record token usage per call so a run's cost is measured rather than estimated.

## Out of scope

- The second PRD (TodoMVC or WebPark) until the unit is fixed; the labeling format would change
  under it.
- Any gate, CI job, or published rate.

## Risks

- The 49 FR-level labels are discarded. That is the largest single loss in this project so far, and
  the reason to decide the unit before labeling anything else.
- Criteria are numbered by hand, so an author who renumbers silently invalidates labels. The data
  invariants check that rows follow the PRD, not that the PRD's own numbers are stable across
  versions.
- The suite grows from 25 cases to 38, so every designer run and every automation pass gets slower.
- `case-20-ui -> FR-UI-01` is the last standing disagreement and it is an FR-level artifact: the
  case mentions its third criterion only in `notes`, and the judge has no rule for "this case did
  not execute every criterion it claims". AC-level makes the case impossible; FR-level would need a
  new judge rule.

## Open questions

- Does `duplicated` stay a human-only analysis field, or become a CODE check now that one
  requirement per case is enforced? Three legacy labels remain in the dataset.
- Is grounding against the criterion enough, or does a criterion also need an "observable result"
  check? `case-13` was once failed for exactly that reason.

## Comments

Opened at the end of the session that produced the PRD v0.4/v0.5 corrections, the judge metric
rename, and the data invariant tests. The decision it waits on is a product one: whether a test
suite should be one journey per requirement or one check per criterion.
