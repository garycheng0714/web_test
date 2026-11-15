# 17: Fix four doc lines that drifted

**What to build:** Correct four one-line drifts left by earlier moves. No behaviour changes.

**Blocked by:** Nothing.

**Status:** ready-for-agent

## Why

| file | says | reality |
| --- | --- | --- |
| `evals/designer/designer_eval/__init__.py` | "Designer eval building blocks used by `run_eval.py`." | five CLIs use it (`run_eval`, `run_judge`, `export_labels`, `report`, `build_claims`) |
| `evals/designer/report.py:394` | `--run` help: "run id under `.scratch/designer-evals/runs/`" | `evals/designer/runs/` |
| `evals/designer/export_labels.py:99` | same help text | same |
| `evals/designer/judge/data/README.md:39-40` | `archive/automationexercise-fr`, `archive/register-login` | the datasets live at `evals/designer/judge/archive/…`, i.e. `../archive/…` from `data/` |

The first three are wrong for anyone who reads the code; the fourth would send a reader to a directory that does not exist.

## Tasks

- [ ] Rewrite the `designer_eval/__init__.py` docstring to name what it is, not one consumer.
- [ ] Fix the two `--run` help strings to `evals/designer/runs/`.
- [ ] Fix the archive paths in `judge/data/README.md` (either `../archive/…` or "archived under `judge/archive/`", whichever reads better in place).
- [ ] `uv run ruff check evals` and `uv run pytest tests/designer_evals` green.

## Out of scope

- The `evals/designer/README.md` layout block: it was updated in the dataset/labels refactor, and it correctly lists `designer_eval/`, `judge/data/`, `judge/runs/`, `phoenix/`, `runs/`.
- `.scratch/**` historical tickets that quote the old paths.

## Risks

- None: documentation only.
