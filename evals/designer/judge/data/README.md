# Judge data

A small, committed dev set for the semantic judge (`evals/designer/judge.py`). Each dataset is one
directory with the PRD text and one row per HUMAN-labeled claim:

```text
<dataset>/prd.md       # the PRD text as it was when the runs were generated
<dataset>/claims.jsonl # claim_id, requirement_id, case_id, requirement_text, case_markdown,
                       # human_label, human_mode, human_reason, source_run
```

## Provenance

Both datasets were built from runs on `feature/designer-evals-claims`, before the PRDs were
normalized (commit `d59813f`). The PRD copies come from `d59813f^`.

| dataset | source runs | claims | fails |
| --- | --- | --- | --- |
| `automationexercise` | `old-skill-automationexercise-20261029` (54), `house-automationexercise-20261029` (31) | 85 | 27 |
| `register-login` | `register-login-20261029T070829Z` | 7 | 0 |

Both datasets use the same automationexercise PRD in the first case, so this is a **dev set only**:
a by-PRD train/dev/test split needs 5-6 PRDs. `register-login` contributes only passes, so it can
check TNR but not TPR.

The run directories themselves stay local (`evals/designer/runs/` and
`evals/designer/judge/runs/` are gitignored).
