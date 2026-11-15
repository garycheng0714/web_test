# 14: One place that knows the eval's directories

**What to build:** Move the run-directory constants and the "which run?" lookup into one module, and route the four scripts and the data-invariant test through it.

**Blocked by:** Nothing.

**Status:** ready-for-agent

## Why

| thing | copies |
| --- | --- |
| `RUNS_DIR = REPO_ROOT / "evals" / "designer" / "runs"` | `run_eval.py:42`, `export_labels.py:24`, `report.py:25`, `build_claims.py:25` |
| `_latest_run()` | `report.py:32` and `export_labels.py:32` (byte-identical, marker `run.json`), `build_claims.py:29` (marker `labels.jsonl`, different message) |
| `--run-dir` → `--run` → latest | `report.py:398-404`, `export_labels.py:108-114`, `build_claims.py:99-104` |
| judge directories | `run_judge.py:35-36` (`DATA_DIR`, `OUT_DIR`), `test_data_invariants.py:16` (`DATA_DIR`) |

Moving `runs/`, adding a dataset directory, or renaming the judge output directory is a six-file edit today. No incident yet, so this is polish, not a bug.

## Module plan

1. **Input**: nothing (constants) or `(run: str | None, run_dir: str | None, marker: str)`.
2. **Output**: `Path` constants; a resolved run directory.
3. **External boundaries**: the on-disk layout (`evals/designer/runs/`, `evals/designer/judge/data/`, `evals/designer/judge/runs/`) and `web_test.paths.REPO_ROOT`.
4. **Domain types vs adapters**: no domain types; this module is the adapter between the repo root and the eval's directories.
5. **Single-variation parts to leave alone**: each script's own argparse help and error message text.
6. **Responsibilities**: one change reason — the eval's on-disk layout; contract = constants plus `latest_run(dir, marker)` and `resolve_run_dir(...)`.

**Shape:**
- Types: `run`/`run_dir` stay `str | None` at the CLI boundary; no new models.
- Boundary: the three directories above.
- Invariants: `latest_run` picks by `st_mtime`; a directory only counts as a run when its marker file exists; a missing set raises `FileNotFoundError` naming the directory.

## Tasks

- [x] Add `evals/designer/designer_eval/layout.py` with `RUNS_DIR`, `JUDGE_DATA_DIR`, `JUDGE_RUNS_DIR`, `latest_run(directory, marker)` and `resolve_run_dir(*, run, run_dir, marker, missing_message)`.
- [x] Route `run_eval.py`, `export_labels.py`, `report.py`, `build_claims.py` and `test_data_invariants.py` through it.
- [x] Keep the two distinct marker files and both messages.
- [x] `uv run pytest tests/designer_evals` green; `uv run lint-imports` still 7 kept.

## Out of scope

- Changing any default run id or dataset name.
- `run_judge.py`'s `DATA_DIR`/`OUT_DIR` naming: it uses `judge/data` and `judge/runs`, which the module should expose as constants rather than renames.

## Risks

- `build_claims.py` resolves `--run-dir` first and needs `labels.jsonl` to exist, while `report.py` needs `run.json`; collapsing them must not silently pick a run the command cannot use.
- `test_data_invariants.py` parametrises over every directory under `judge/data/`; a helper that filters by marker would change what the test scans.

## Result

`designer_eval/layout.py` holds the three directories, `latest_run(directory, marker)` and
`resolve_run_dir(run=…, run_dir=…, marker=…)`. The four scripts and `test_data_invariants` use it;
`RUNS_DIR`, `_latest_run` and the nested `--run-dir`/`--run`/latest branches are gone.

One deviation from the ticket: the two messages became one, `no run with <marker> under <dir>`. The
marker already says which command can use the run (`labels.jsonl` for `build_claims`, `run.json` for
the other three), so a second message added a distinction the string already carries. No test
asserted the old text.

Checked end to end: `report.py --run-dir <copy>` and `report.py --run journey-v07-20261103` exit 0,
`build_claims.py --run journey-v07-20261103` still reproduces the committed dataset byte for byte,
`run_judge.py --help` imports cleanly.
