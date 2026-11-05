# 07: Rewrite the PRD's acceptance criteria as journeys, then rebuild the fixture

**What to build:** One acceptance criterion per journey, so every case in the suite is one journey
and the AC text is the claim. Rewrite the nine multi-AC requirements of the working PRD, run the
designer once on the result, check that the run emits one case per criterion, label the 27 claims,
and rebuild the judge fixture. The claim unit stays `(case, requirement)`; only the PRD's criteria
change.

**Blocked by:** Nothing. The schema work is ticket 06 and is not needed here.

**Status:** ready-for-agent

## Decisions this ticket encodes

- An AC is one journey: a start state, product-owned actions, and one observable end state. A
  shared fixture may split into two ACs; a shared sequence may not (the second AC's start state
  comes from the first AC's steps).
- Actions count only when the product owns them. Scrolling with the browser is not an action, so
  TC26 is dropped and `FR-UI-01` keeps one AC.
- Exact strings an assertion needs go into the AC text; the FR body keeps page facts (fields,
  options, copy) that several ACs share.
- The judge keeps its current input: the whole PRD plus the claimed requirement. No prompt change.
- One AC per journey means 23 requirements have exactly one AC, so `FR` and `AC` name the same
  thing for them. The two-AC requirements are `FR-ACC-04` and `FR-ORD-01`.

## Shape

- Types: none. `Case`, `DesignOutput`, `LabeledClaim`, and `AcceptanceCriterion` keep their shape.
- Boundary: the rendered AC bullets of `.scratch/automationexercise/prd.md` and the §9 traceability
  matrix. The committed fixture already reads that PRD live (commit `be2b6b8`), so the edit reaches
  the judge with no copy to sync.
- Invariants: every requirement keeps at least one AC; every collapse keeps `AC-1` and deletes the
  later numbers, so no AC is renumbered; every case in the new run maps to exactly one AC; every
  AC in the PRD has exactly one case; the fixture holds rows from one source run only.

## State when this ticket was opened

- PRD v0.5: 25 requirements, 38 criteria. Nine requirements carry 2-3 criteria: `FR-ACC-01` (3),
  `FR-ACC-04` (2), `FR-PRD-03` (2), `FR-PRD-05` (2), `FR-CART-01` (3), `FR-ORD-01` (2),
  `FR-ORD-02` (2), `FR-ENG-01` (3), `FR-UI-01` (3). The other 16 carry one.
- `FR-CART-01 AC-3` (total = price × quantity) needs a quantity other than 1, which is
  `FR-CART-02`'s action; it is a checkpoint on the cart row, not a journey of its own.
- The judge dataset reads the working PRD by requirement id; rows no longer carry a requirement
  text, so a PRD edit cannot leave stale text behind.
- `evals/designer/judge/data/automationexercise/claims.jsonl` holds 82 rows from two pre-ticket-30
  skills; 49 are single-requirement rows (17 fail, 32 pass). They are an FR-level snapshot.
- `run_eval.py` still defaults to `prd/register-login.md`.

## Tasks

- [x] Rewrite the nine multi-AC sections in `.scratch/automationexercise/prd.md`:

  | FR | now | after | why |
  | --- | --- | --- | --- |
  | `FR-ACC-01` | 3 | 1 | signup form → create account → logged in is one sequence |
  | `FR-ACC-04` | 2 | 2 | two branches from one fixture; add "still a guest" to `AC-2` |
  | `FR-PRD-03` | 2 | 1 | the result list's contents belong to the same search |
  | `FR-PRD-05` | 2 | 1 | switching brands happens inside one visit |
  | `FR-CART-01` | 3 | 1 | rows and the total are checkpoints of one cart state |
  | `FR-ORD-01` | 2 | 2 | guest and member are two journeys |
  | `FR-ORD-02` | 2 | 1 | one checkout page |
  | `FR-ENG-01` | 3 | 1 | dialog → message → home is one sequence |
  | `FR-UI-01` | 3 | 1 | drop `AC-3`; cite only TC25 |

- [x] Add a v0.6 note to the PRD header defining AC as one journey, and rewrite the `AC =` line in
      §4.
- [x] Remove the TC26 row from §9 and the TC26 citation from `FR-UI-01`.
- [x] Keep `uv run pytest tests/designer_evals` green; the fixture resolves rows by requirement id,
      so 38 → 27 needs no data change.
- [x] Start Phoenix (`uvx arize-phoenix serve`) and run the designer once on the rewritten PRD with
      an explicit `--run-id` (`run_eval.py` would otherwise name the run `prd-<timestamp>`).
- [x] Gate before labeling: the run must emit 27 cases, each on exactly one requirement, with no
      multi-requirement case and no duplicate. If it emits 25, the designer still works one case per
      FR: add the "one AC per case" rule to the house skill and run it again (a second paid call).
- [ ] Label the 27 claims in Phoenix: `claim_alignment` on each, plus `claim_failure_mode` and
      `claim_reason` on failures. Modes: `wrong_actions`, `prd_gap`, `case_assertion`,
      `wrong_assertion_to_requirement`, `incomplete_journey`, `duplicated` (legacy only).
- [ ] Export the labels and write the new `claims.jsonl`. Move the old 82-row file to
      `evals/designer/judge/archive/automationexercise-fr/`; do not delete it and do not mix rows
      from both files in one metric.
- [ ] Run the judge three times with distinct run ids, take the majority verdict per claim, and
      report `fail_recall`, `pass_specificity`, the confusion counts, and the Wilson intervals.
- [ ] Record token usage per call in `run.json` and the judge runs, so the baseline's cost is a
      measurement rather than an estimate.

## Out of scope

- `ac_ids`/`criterion_id` on `Case`, the derived `requirement_ids`, and the writer/reader changes
  (ticket 06).
- The skill's AC traceability rule. Add it only if the gate above shows 25 cases.
- `prd/register-login.md` (8 ACs, left as-is), `prd/login-smoke.md`, and `prd/live-evidence.md`
  (historical probes).
- Moving the judge to AC-level claims. The 27 rows re-key mechanically later because the mapping is
  1:1.
- Any gate, CI job, or published rate.
- The `run_eval.py` default and the archived `register-login` dataset (ticket 08).

## Paid actions

- One designer call for the gate run; a second only if it returns 25 cases.
- 27 claims × 3 judge runs = 81 judge calls.
- Human labeling of 27 claims.

Confirm the budget before the first designer call.

## Risks

- The designer may still emit one case per FR (25), which costs a second run and a skill edit.
- The 82 old rows are superseded. They stay archived for history, but no report may combine them
  with the new fixture, because the PRD text and the case distribution differ.
- The collapsed AC keeps `AC-1`, so this rewrite cannot renumber anything. A later edit that removes
  a middle AC must keep the gap, or every AC-level label keyed on it changes meaning.
- `run_eval.py` derives the run id from the PRD's stem; with `--prd .scratch/automationexercise/prd.md`
  that stem is `prd`, so pass `--run-id`.
- Phoenix must be running before the designer call, or the run records no units.

## Open questions

- Does the new fixture keep the dataset name `automationexercise` (archive the old rows, keep the
  live-PRD link), or take a new name? A new name breaks `dataset_prd`'s "dataset name = PRD
  directory name" mapping and would need its own PRD copy.
- Are the three baseline runs all at the default temperature? The spec records that temperature 0
  does not remove variance, so three runs stay mandatory either way.

## Flow

```text
rewrite PRD ACs (38 -> 27)
  │
  ▼
one designer run
  │
  ├─ 27 cases, one AC each ──► label 27 claims ──► new claims.jsonl
  │                                              │
  └─ 25 cases ──► add the AC rule, run again       ▼
                                            judge x3 ──► baseline
```

## Comments

Opened 2026-11-03 from the session that decided the AC unit. The decision was to fix the PRD and
the fixture first, at `(case, requirement)` granularity, and defer the AC-level schema to ticket 06.
Ticket 06's "rebuild the fixture" task is this ticket; 06 starts after it.

2026-11-03: PRD rewritten (38 -> 27) and the gate run done as `ac-journey-20261103` on
`openai-chat:deepseek-v4.1-flash`, project `web-test-designer-eval`.

| | result |
| --- | --- |
| cases | 27 |
| claims | 27 (one per case) |
| requirements | 25, all covered |
| requirements per case | 1 for all 27 |
| duplicate cases | 0 |
| invalid or non-requirement ids | 0 |
| usage | prompt 16,889 / completion 12,805 / cache read 7,552 / total 29,694 |

So the gate passed on the first run: every case is one journey and `FR-ACC-04` / `FR-ORD-01`
contributed their two branches. The skill fallback was not needed.

The run exited 1 after writing its artifacts: the CODE annotations POST returned 404 because the
span ids were not indexed yet moments after creation. Re-sending the same 27 annotations a minute
later succeeded, so the cause is indexing lag, not a bad payload. `run_eval.py` now retries the
annotation write three times, two seconds apart.

Next: label 27 claims in Phoenix, then four paid steps — export, new `claims.jsonl`, judge x3.

2026-11-03, v0.7: the model changed again while reviewing the run. An AC that only restates its
requirement is a redundant layer, so a requirement is now the journey itself and the PRD has no AC
labels at all. The two requirements that carried two criteria became two requirements each:

- `FR-ACC-04` 登入成功 and the new `FR-ACC-07` 登入失敗
- `FR-ORD-01` 前往結帳(已登入) and the new `FR-ORD-05` 前往結帳(未登入)

Requirements went 25 -> 27; criteria went 27 -> 0. The plan and the claim unit are unchanged:
`(case, requirement)`, which is what the eval already does. `parse_requirements` still reads ACs for
`prd/register-login.md`, so the parser stays; only
`test_every_requirement_has_an_acceptance_criterion` was deleted.

The gate re-ran as `journey-v07-20261103`: 27 cases, 27 requirements, one requirement per case, no
duplicates, 54 units (27 requirement + 27 claim), 27 annotations. Usage: prompt 57,023 / completion
17,990 / cache read 25,856 / total 75,013. Compared with the v0.6 run, the only change in the
requirement sets is the two new ids; the other 25 cases map one-to-one.

So the target is 27 claims over 27 requirements, and the fixture keeps the requirement id as its
key.

2026-11-05: the failure-mode taxonomy changed before labeling, because the old four were built for
multi-requirement cases:

- `wrong_scenario_to_requirement` is renamed `wrong_actions` and now also covers "the journey was
  done by the case's preconditions". The old name read as "wrong scenario chosen", which hid that
  case.
- `undefined_behavior` split by the owner of the fix: `prd_gap` (the journey needs a behaviour the
  PRD does not state) and `case_assertion` (the case invented a value or asserted something
  undecidable).
- `incomplete_journey` is new: the case performs the journey but never asserts a result the
  requirement states. Nothing measured that before.
- `duplicated` stays as a legacy value; a case can no longer carry a second requirement.

Decision order: `wrong_actions` -> `prd_gap` -> `case_assertion` -> `wrong_assertion_to_requirement`
-> `incomplete_journey` -> `duplicated`. The first one is about the actions; the rest are about the
assertions.

The judge's `SYSTEM_PROMPT` now carries a fourth rule for `incomplete_journey`, and its third rule
no longer mentions acceptance criteria. Page furniture, field lists, element presence, and
form-entry mechanics are explicitly not results, or the completeness rule would fail every
element-presence requirement. The prompt hash changes, so no earlier judge run is comparable.

Phoenix: the `claim_failure_mode` annotation config on `web-test-designer-eval` now lists the six
current values, plus `wrong_scenario_to_requirement` and `undefined_behavior` as legacy values so
the archived annotations still render, plus `N/A`.
