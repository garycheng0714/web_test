# 12: One JSONL helper for the eval's boundary files

**What to build:** Move the "read a JSONL file into models" and "write models as JSONL" idiom into one helper, and route the five sites through it.

**Blocked by:** Nothing.

**Status:** ready-for-agent

## Why

Five sites repeat the same two lines, and the policy they encode lives in five places:

| site | operation |
| --- | --- |
| `designer_eval/labels.py:42` (`write_labels`) | write, `exclude_none=False` |
| `designer_eval/judge.py:300` (`write_records`) | write, `exclude_none=False` |
| `evals/designer/build_claims.py:114` | write, `exclude_none=False`, inline |
| `designer_eval/labels.py:34` (`read_labels`) | read, skip blank lines |
| `designer_eval/dataset.py:70` (`load_dataset`) | read, inline, mixed with filtering and validation |

The policy is: one row per line, `exclude_none=False` (the datasets rely on `"human_mode": null`), blank lines skipped, a malformed line raises. Changing any of it means making the same edit five times, and the two writers already name `exclude_none=False` explicitly while `dataset.py` reads without it.

## Module plan

1. **Input**: a `Path` and a Pydantic row type; or a `Path` and a list of rows.
2. **Output**: `list[Row]`; or the written file.
3. **External boundaries**: `labels.jsonl`, `claims.jsonl`, `judgements.jsonl` — files only.
4. **Domain types vs adapters**: the row models stay where they are (`AnnotationRow`, `LabeledClaim`, `JudgeRecord`); the helper owns no model and is a pure adapter.
5. **Single-variation parts to leave alone**: `run.json`, `units.json`, `design.json` are single pretty-printed documents, not JSONL; they keep `model_dump_json(indent=2)`.
6. **Responsibilities**: one change reason — the serialization policy of line-delimited model files; contract = `(path, model) -> rows` and `(path, rows) -> file`.

**Shape:**
- Types: `RowT = TypeVar("RowT", bound=BaseModel)`; no new models.
- Boundary: the three JSONL files above.
- Invariants: one row per non-blank line; output ends with a newline; `None` fields are written; a malformed line raises `pydantic.ValidationError` (a `ValueError`, so the CLIs keep their `failed to read …` path).

## Tasks

- [x] Add `evals/designer/designer_eval/jsonl.py` with `read_rows(path, model)` and `write_rows(path, rows)`.
- [x] Route `labels.read_labels` / `write_labels`, `dataset.load_dataset`, `judge.write_records` and `build_claims.main` through it.
- [x] Leave `load_dataset`'s single-FR filter and its "claims a requirement the PRD does not define" error where they are.
- [x] Add one test: a file with a blank line and a `null` field round-trips, and a malformed line raises.
- [x] `uv run pytest tests/designer_evals` green; `uv run lint-imports` still 7 kept.

## Out of scope

- `run.json`, `units.json`, `design.json`.
- The contents of `judge/data/**` and `judge/archive/**`.

## Risks

- The committed datasets must stay byte-identical. Verify by rebuilding one with `build_claims.py --run journey-v07-20261103` and diffing against `judge/data/automationexercise/claims.jsonl`.
- `judge.write_records` writes into gitignored `judge/runs/`, so a trailing-newline change there is only visible by opening the file.

## Result

`designer_eval/jsonl.py` owns the idiom: `read_rows[RowT](path, model)` and `write_rows(path, rows)`
(one row per line, `exclude_none=False`, blank lines skipped, parent directory created).

`labels.read_labels`, `dataset.load_dataset`, `judge.write_records`, `build_claims.main` and
`export_labels.main` all go through it. `labels.write_labels` was deleted: it had one caller and
only bound the model, so the caller names `write_rows` directly.

`tests/designer_evals/test_jsonl.py` covers the round trip, a `null` field, blank lines and a
malformed row. Rebuilding `journey-v07-20261103` still produces a byte-identical
`judge/data/automationexercise/claims.jsonl`.
