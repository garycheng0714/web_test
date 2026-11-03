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
- [ ] Start Phoenix (`uvx arize-phoenix serve`) and run the designer once on the rewritten PRD with
      an explicit `--run-id` (`run_eval.py` would otherwise name the run `prd-<timestamp>`).
- [ ] Gate before labeling: the run must emit 27 cases, each on exactly one requirement, with no
      multi-requirement case and no duplicate. If it emits 25, the designer still works one case per
      FR: add the "one AC per case" rule to the house skill and run it again (a second paid call).
- [ ] Label the 27 claims in Phoenix: `claim_alignment` on each, plus `claim_failure_mode` and
      `claim_reason` on failures.
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
