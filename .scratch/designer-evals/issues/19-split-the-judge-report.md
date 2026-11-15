# 19: Split the judge report out of `judge.py`

**What to build:** Move the markdown report out of the judging module, so `judge.py` reads as "how one
claim is judged" and nothing else.

**Blocked by:** Nothing.

**Status:** ready-for-agent

## Why

`judge.py` carried 70 lines of markdown tables (`format_rate`, `render_report`) between `score` and
`write_records`. The earlier decision was to leave them there, on the grounds that the metrics block
never changed on its own (`git log -L` over 183-296 shows two commits, both shared with the prompt).
That argument holds for `score`, not for the report: a layout change has no reason to touch the
prompt, the schema or the call.

Two clashes made the split worth the files:

- `render_report` needs `JudgeMetrics` and `JudgeRecord`, which lived in `judge.py`. Moving the
  renderer alone would leave `judge_report -> judge`, so the new module would still read as part of
  the judging code.
- `JudgeMetrics` depends on `JudgeRecord` (its `disagreements` list), so both belong on the same
  side of the seam.

## Shape

- Types: `JudgeRecord` and `JudgeMetrics` move to `judge_records.py` unchanged.
- Boundary: none; no file format changes.
- Invariants: `judge_records` imports only `pydantic` and `dataclasses`; `judge_report` imports
  `judge_records` and nothing else; `judge.py` never imports `judge_report`.

## Tasks

- [x] Move `JudgeRecord` and `JudgeMetrics` to `evals/designer/designer_eval/judge_records.py`.
- [x] Move `format_rate` and `render_report` to `evals/designer/designer_eval/judge_report.py`.
- [x] Leave `write_records` in `judge.py`: it stores what `run_one` produced, which is the judge's
      own output step, not presentation.
- [x] Update `run_judge.py` and `test_judge.py` imports.
- [x] Note the new modules in `evals/designer/README.md`'s layout block.

## Out of scope

- Splitting `test_judge.py`; the tests already read as separate behaviours, and one file keeps the
  fixtures in one place.
- Moving `score` / `group_by_source`.
- A lint-imports contract for the internal layering (ADR-0010 keeps that as convention).

## Risks

- Three modules for a dev-only eval. The seam is justified only by the leaf rule: if a fourth file
  appears for the same reason, the split is wrong.
- `judge_records.py` is now a leaf both modules import; a change to `JudgeMetrics` touches it, and
  both consumers recompile.

## Result

```text
judge.py           193 lines   prompt, output schema, load_examples, run_one, score,
                              group_by_source, write_records
judge_records.py    49 lines   JudgeRecord, JudgeMetrics
judge_report.py     72 lines   format_rate, render_report
```

`render_report` is byte-identical to the previous version on three fixtures: mixed verdicts with a
disagreement and two source runs, an all-pass set (rate `n/a`), and an empty set. 391 tests,
basedpyright clean, 7 contracts kept.

## Comments

2026-11-15: the human overrode the earlier "leave it" decision, for the reading reason rather than a
change-frequency reason. Chose the leaf layout (three files) over a two-file split so the report does
not import the judging module at all.
