# Judge data

A small, committed dev set for the semantic judge (`evals/designer/run_judge.py`). Each dataset is one
directory with the PRD text and one row per HUMAN-labeled claim:

```text
<dataset>/prd.md       # the PRD text the labels are judged against
<dataset>/claims.jsonl # claim_id, requirement_id, case_id, case_markdown,
                       # human_label, human_mode, human_reason, source_run
```

The requirement text is not stored per row: `load_examples` reads it from the PRD by
`requirement_id`, so editing a PRD cannot leave a row holding stale text. The judged dataset
(`automationexercise`) has no `prd.md` of its own; `dataset_prd` reads the repo's
`.scratch/automationexercise/prd.md` instead.

Superseded datasets are moved to `evals/designer/judge/archive/`, outside `data/`, because
`test_data_invariants` scans every directory under `data/`.

## Provenance

Rows are built with `evals/designer/build_claims.py`, which joins a run's `units.json` with the
HUMAN annotations in its exported `labels.jsonl`. The committed file is then corrected in review;
the builder is the starting point, not the authority.

| dataset | source run | claims | fails |
| --- | --- | --- | --- |
| `automationexercise` | `journey-v07-20261103` | 27 | 0 |
| `todomvc` | `todomvc-v03-20261106` | 22 | 1 |

Archived, not judged:

| dataset | source runs | claims | fails |
| --- | --- | --- | --- |
| `archive/automationexercise-fr` | `old-skill-automationexercise-20261029` (52), `house-automationexercise-20261029` (30) | 82 | 30 |
| `archive/register-login` | `register-login-20261029T070829Z` | 7 | 0 |

Two PRDs are judged, so this is still a **dev set**: a by-PRD train/dev/test split needs 5-6 PRDs.
Both sets are pass-heavy; `automationexercise` has no failures at all, and `todomvc` has one, whose
label compares the PRD to the app rather than the case to the PRD.

`register-login` was the eval's default PRD by habit, not by design: it was the first complete PRD in
the repo. Its `FR-ACC-01` still carries three staged criteria, so a designer run on it either splits
one journey into three cases or drops two. Tickets 06 and 08 retired it.

## Label history

**2026-11-05, PRD v0.7 and a new unit.** The working PRD became one requirement = one journey, with
no acceptance-criterion labels (25 requirements became 27). The 82-row set above was archived
unchanged; the new set is 27 claims from `journey-v07-20261103`, all labeled `pass`. The failure-mode
vocabulary changed at the same time, so `wrong_scenario_to_requirement` and `undefined_behavior` only
appear in the archived rows; see `evals/designer/spec.md` for the current six.

**2026-11-03, rubric.** Three passing claims asserted content the PRD did not state and were
relabeled `fail` (`undefined_behavior`): `case-14 -> FR-PRD-04`, `case-21 -> FR-CART-02`,
`case-30 -> FR-ORD-02`. The rule lives in `evals/designer/spec.md`.

**2026-11-03, PRD v0.4 alignment.** `prd.md` now matches the working PRD v0.4, and every row's
requirement text was refreshed from it (the per-row copy has since been dropped: the PRD is read by
id). Labels changed only where the new text decides the verdict:

- `case-13 -> FR-PRD-04` and `case-14 -> FR-PRD-04` became `pass`: v0.4 states that the category
  page lists only the selected subcategory's products.
- `case-14 -> FR-CART-02` and `case-21 -> FR-CART-02` stay `fail`, but the mode moved to
  `wrong_assertion_to_requirement`: the total price is now defined by FR-CART-01 AC3, so it is no
  longer undefined, but it still does not verify FR-CART-02.
- `case-43 -> FR-UI-02` was dropped: v0.3 removed that requirement.
- The two multi-requirement `FR-ACC-02` rows whose case already had a merged `FR-ACC-01` claim were
  dropped. One single-requirement row was remapped from `FR-ACC-02` to `FR-ACC-01`; its case yaml
  still cites the pre-merge id, because the case is the artifact under test and is not rewritten.

## Source of truth

The committed dataset in this directory is the source of truth for the judge, not Phoenix. The
labels were corrected in review after they were first annotated (the v0.4 alignment, the boundary
ruling), and Phoenix still holds the original values. Re-exporting either historical run rebuilds a
`labels.jsonl` that would silently revert those corrections, so do not rebuild this directory from
Phoenix. Phoenix remains the labeling UI for new runs; `build_claims.py` turns a fresh export into
candidate rows, and those rows are reviewed before they replace this file.

The run directories themselves stay local (`evals/designer/runs/` and `evals/designer/judge/runs/`
are gitignored).
