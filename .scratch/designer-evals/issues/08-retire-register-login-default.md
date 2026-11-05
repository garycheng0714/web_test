# 08: Retire `register-login` as the eval's default PRD

**What to build:** Point the designer eval at the working PRD, and archive the `register-login`
judge dataset. The working PRD is `.scratch/automationexercise/prd.md`; `register-login` was the
eval's first input by habit, not by design, and it no longer follows the AC rule.

**Blocked by:** Nothing.

**Status:** ready-for-agent

## Why

`run_eval.py`, `export_labels.py`'s docstring, both Phoenix probes, and the README all default to
`prd/register-login.md`. That default predates the working PRD: `register-login` was the first
complete PRD in the repo (v0.2, reverse-engineered from a live walkthrough) and the designer eval
inherited it in `e1f0b85` without a stated reason. It has two costs now:

- It is not the PRD the judge dataset and the baseline use, so a default run measures a different
  document than the one under test.
- Its `FR-ACC-01` keeps three staged criteria. Once the skill reads criteria, a run on it either
  splits one journey into three cases or silently drops two criteria. Ticket 07 leaves it as-is, so
  the trap stays live as long as it is the default.

The dataset is a second cost: its 7 rows are all passes and all `requirement_id`-shaped. Keeping it
in `judge/data/` forces the fixture model to carry two shapes once the working fixture gains a
criterion field.

## Shape

- Types: none.
- Boundary: `run_eval.py`'s `--prd` default, `evals/designer/README.md`, and
  `evals/designer/judge/data/README.md`. The archive moves to
  `evals/designer/judge/archive/register-login/` — outside `data/`, because `data/` is scanned for
  dataset directories and an `archive/` inside it would be read as one.
- Invariants: the default PRD runs without an extra argument; the archived dataset is still present
  and readable; `test_data_invariants` scans only live datasets.

## Tasks

- [x] Change `run_eval.py`'s `--prd` default from `prd/register-login.md` to
      `.scratch/automationexercise/prd.md`.
- [x] Update `evals/designer/README.md` so its default-run example matches, and say the default is
      the working PRD.
- [x] Move `evals/designer/judge/data/register-login/` to
      `evals/designer/judge/archive/register-login/`; do not delete it.
- [x] Update `evals/designer/judge/data/README.md`: drop the archived dataset from the provenance
      table, and add one line saying where it went and why.
- [x] Keep `uv run pytest tests/designer_evals` green.

## Out of scope

- Rewriting `prd/register-login.md`. It stays at 8 criteria and does not follow the AC rule.
- `prd/login-smoke.md` and `prd/live-evidence.md`; mark them as historical probes when they are next
  touched.
- The fixture rebuild and the baseline (ticket 07).
- The AC-level schema (ticket 06).

## Risks

- Anyone who relied on `--dataset register-login` loses that name. Nothing in CI uses it; the
  invariant tests simply stop scanning it.
- The archived dataset still resolves against its own `prd.md` snapshot, so it stays readable. If it
  is ever revived, the absent criterion field has to be added at that point.
- Changing a CLI default is silent: scripts that relied on the old default now measure another PRD.
  The README line is the only warning.

## Comments

Opened 2026-11-03. Decided in the same session as ticket 07: the working PRD is the eval's primary
input, and `register-login` has no reason to be the default. The 7-row dataset contributes only
passes, so it cannot check the fail class on its own.

## Result

`run_eval.py` now defaults to `.scratch/automationexercise/prd.md`; the README shows that default and
says why an explicit `--prd prd/register-login.md` is not the unit the eval measures any more. The
7-row dataset moved to `evals/designer/judge/archive/register-login/`, and the data README lists it
under "Archived, not judged" instead of the provenance table.

`test_data_invariants` now scans one dataset. Tests: 368 passed.
