# 18: Decide whether `evals/designer/phoenix/` stays

**Type:** task (decision)

**What to build:** Nothing yet. Choose one of the three options below for the probes under `evals/designer/phoenix/`, then carry it out.

**Blocked by:** Nothing.

**Status:** resolved

## Why

`spike.py` (157), `late_child_probe.py` (109) and `spike_register.py` (93) are 359 lines the package does not use:

- their own `README.md` opens with "Throwaway spike";
- last touched in `dd4b2e5` (2026-11-02);
- excluded from `basedpyright` (`pyproject.toml`, `exclude = [… "evals/designer/phoenix"]`), so they have never been type-checked;
- `.scratch/designer-evals/reviews/2026-11-02-run-eval-refactor.md:38` already recorded that "endpoint 邏輯仍有四份：`phoenix/spike.py`、`late_child_probe.py`、`spike_register.py`、`export_labels.py`".

They still sit inside Ruff's `include` (`evals/designer/**/*.py`), so they are the only code in the eval that is linted but not type-checked.

Their findings are written down: `learn/evals/reference/phoenix.md`. The runnable scripts are not referenced by any test, CLI, workflow or doc outside their own README.

## Options

1. **Delete them.** Their knowledge survives in `learn/evals/reference/phoenix.md`; git keeps the scripts if they are ever wanted, and deleting is one commit.
2. **Keep them, mark them historical.** Add a line to `phoenix/README.md` saying they are not maintained and exist to reproduce the 2026-11 observations; optionally also exclude them from Ruff so the "linted but not typed" asymmetry is explicit.
3. **Keep them maintained.** Then they need the `base_url` from ticket 13 and a place in `basedpyright`; that is work with no consumer.

Option 1 is the smallest state; option 2 costs one paragraph. Option 3 is not recommended: nothing runs them.

## Tasks

- [x] Pick an option: **1, delete them** (decided by the human, 2026-11-15).
- [x] If deleting: remove `evals/designer/phoenix/` and the layout line in `evals/designer/README.md`; keep the `learn/` reference.
- [x] If keeping: not applicable.
- [x] `uv run ruff check evals` and `uv run pytest tests/designer_evals` green either way.

## Out of scope

- `learn/evals/reference/phoenix.md`: a course reference, not project code.
- `evals/designer/README.md`'s `phoenix/` entry unless option 1 is chosen.

## Risks

- Deleting loses the runnable probes. If the Phoenix instrumentation is ever debugged again (the "late child span" and "register span" questions are already answered in `learn/`, but a new Phoenix version may reopen them), the scripts have to be rewritten from that reference.
- Keeping them without an owner means the next Phoenix upgrade silently breaks them, and nobody finds out because nothing runs them.

## Result

`evals/designer/phoenix/` is gone (four files, 507 lines including its README). Also removed the
`evals/designer/phoenix` entry from `[tool.basedpyright] exclude`, which existed only for those
files, and the `phoenix/` line from the README's layout block.

The findings stay in `learn/evals/reference/phoenix.md`; the scripts are in this commit's parent in
git history if they are ever needed again. `uv run ruff check evals`, `uv run --group eval
basedpyright` (0 errors), `uv run lint-imports` (8 kept) and 391 tests all still pass; nothing
imported the probes.
