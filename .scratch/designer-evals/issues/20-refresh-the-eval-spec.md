# 20: Refresh the eval spec's Data and Ticket map

**What to build:** Bring `evals/designer/spec.md` back in line with the eval as it now runs. Documentation only.

**Blocked by:** Nothing.

**Status:** ready-for-agent

## Why

`spec.md` is the eval's contract — "The contract lives in [`spec.md`](spec.md)" is the first line of the README — and three of its sections describe a state the eval left behind in tickets 08, 09 and 11:

| line | says | reality |
| --- | --- | --- |
| 68-69 | PRDs: `prd/register-login.md` (FR-ACC-01~06), `prd/login-smoke.md`, `prd/live-evidence.md`; "必要時加 `.scratch/automationexercise/prd.md`" | the working PRDs are `.scratch/automationexercise/prd.md`, `.scratch/todomvc/prd.md`, `.scratch/realworld/prd.md`; the three `prd/` files are historical and no longer the default |
| 73-74 | each run stores `design.json`, `run.json`, `units.json`, rendered markdown | also `prd.md` (`write_results`) and `labels.jsonl` (`export_labels`) |
| 115 | "目前只有一份帶負例的 PRD，judge 只能做 dev (claim-level)" | six datasets over three PRDs: `todomvc` has 1 fail, `todomvc-probe` 15 (mutations, not natural designer output) |
| 178-185 | Ticket map lists 01, 02, 03, 04, 06 and "05 deferred" | tickets 07-19 exist; 06 is still `needs-triage`; 08, 09, 11, 12-17, 19 are done |
| 190 | `Ticket status：needs-triage` under Decisions | that recorded the default when the feature started, and now reads as a live statement |

## Tasks

- [x] Rewrite the `## Data` PRD list: name the three working PRDs under `.scratch/`, and say the `prd/` files are historical inputs (one line, no table).
- [x] Add the two missing run artifacts to the list on line 73.
- [x] Rewrite line 115 so it states what the six datasets actually contain: no natural designer failure in `automationexercise`, `todomvc-v07`, `todomvc-v08` or `realworld`; `todomvc` has one PRD-vs-app failure; `todomvc-probe` is mutation-based and reported separately. Keep the "still short of a by-PRD split" conclusion, which is true.
- [x] Extend the Ticket map to the current numbering, or replace it with a pointer to `.scratch/designer-evals/issues/` (it has drifted once; a pointer cannot drift).
- [x] Make line 190 say it recorded a starting default rather than a live rule.
- [x] `uv run pytest tests/designer_evals` green (nothing should change).

## Out of scope

- The `## Decisions` entries about labels, ids, coverage and judge criteria; they still hold.
- `docs/adr/0010` and the contracts in `pyproject.toml`.
- Rewriting the failure-mode paragraph (81-87): verified against the data, the old names exist only in `judge/archive/automationexercise-fr`, which is what it says.

## Risks

- `spec.md` is 14 KB of prose with interleaved decisions; editing one section can contradict another. Re-read the whole `## Data` and `## Evaluations` after the edit rather than only the changed lines.
- A Ticket map kept by hand will drift again. Preferring a pointer is a deliberate loss of "what is open" at a glance.

## Result

- `## Data` now names the three working PRDs under `.scratch/` (checked: all three exist) and says
  the `prd/` files are historical inputs; the default `--prd` is
  `.scratch/automationexercise/prd.md`, as the code has had it since ticket 08.
- The run artifact list gains `prd.md` and `labels.jsonl`.
- The "only one PRD with failing labels" line now states what the six datasets hold, counted from
  `judge/`: `automationexercise`, `todomvc-v07`, `todomvc-v08`, `realworld` 0 fails; `todomvc` 1;
  `todomvc-probe` 15, reported separately.
- The Ticket map became a pointer to `.scratch/designer-evals/issues/`, with ticket 05's deferred
  decision kept in `## Decisions`, where it already was.
- `Ticket status：needs-triage` now reads as the starting default it was.
- Also removed a dangling "ticket 30" reference on line 113: the numbering in this repo stops at 21,
  so the multi-FR note now says "早期 run 的歷史形狀".

Documentation only; tests unaffected.
