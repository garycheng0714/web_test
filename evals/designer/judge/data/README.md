# Judge data

A small, committed dev set for the semantic judge (`evals/designer/judge.py`). Each dataset is one
directory with the PRD text and one row per HUMAN-labeled claim:

```text
<dataset>/prd.md       # the PRD text the labels are judged against
<dataset>/claims.jsonl # claim_id, requirement_id, case_id, requirement_text, case_markdown,
                       # human_label, human_mode, human_reason, source_run
```

## Provenance

Both datasets were built from runs on `feature/designer-evals-claims`. The rows and the cases inside
them come from the runs as generated; the PRD has since been aligned to v0.4 (see below).

| dataset | source runs | claims | fails |
| --- | --- | --- | --- |
| `automationexercise` | `old-skill-automationexercise-20261029` (52), `house-automationexercise-20261029` (30) | 82 | 31 |
| `register-login` | `register-login-20261029T070829Z` | 7 | 0 |

Both datasets use the same automationexercise PRD in the first case, so this is a **dev set only**:
a by-PRD train/dev/test split needs 5-6 PRDs. `register-login` contributes only passes, so it can
check one class but not the other.

Most automationexercise rows predate ticket 30 (one case per requirement), so `load_examples` skips
multi-requirement cases unless `--include-multi-fr` is passed. The 49 single-requirement rows are the
current target: 18 fail, 31 pass.

## Label history

**2026-11-03, rubric.** Three passing claims asserted content the PRD did not state and were
relabeled `fail` (`undefined_behavior`): `case-14 -> FR-PRD-04`, `case-21 -> FR-CART-02`,
`case-30 -> FR-ORD-02`. The rule lives in `evals/designer/spec.md`.

**2026-11-03, PRD v0.4 alignment.** `prd.md` now matches the working PRD v0.4, and every row's
`requirement_text` was refreshed from it. Labels changed only where the new text decides the
verdict:

- `case-13 -> FR-PRD-04` and `case-14 -> FR-PRD-04` became `pass`: v0.4 states that the category
  page lists only the selected subcategory's products.
- `case-14 -> FR-CART-02` and `case-21 -> FR-CART-02` stay `fail`, but the mode moved to
  `wrong_assertion_to_requirement`: the total price is now defined by FR-CART-01 AC3, so it is no
  longer undefined, but it still does not verify FR-CART-02.
- `case-43 -> FR-UI-02` was dropped: v0.3 removed that requirement.
- The two multi-requirement `FR-ACC-02` rows whose case already had a merged `FR-ACC-01` claim were
  dropped. One single-requirement row was remapped from `FR-ACC-02` to `FR-ACC-01`; its case yaml
  still cites the pre-merge id, because the case is the artifact under test and is not rewritten.

Phoenix still holds the original annotations, so re-exporting these runs would revert every change
above until the Phoenix annotations are replaced.

The run directories themselves stay local (`evals/designer/runs/` and `evals/designer/judge/runs/`
are gitignored).
