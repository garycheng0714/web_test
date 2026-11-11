# 10: Measure the judge's fail recall with a mutation probe

**What to build:** Twenty mutated test cases whose defects are known by construction, labeled by a
human, and judged three times, so the judge has a `fail_recall` number. Kept as a separate dataset;
it never mixes with the designer-run sets.

**Blocked by:** Nothing. Ticket 07's sets are all pass-only, so recall was never measurable.

**Status:** ready-for-human

## Shape

- Types: none. `LabeledClaim` carries the probe rows as it does any other.
- Boundary: `.scratch/designer-evals/probes/` (the review file and the answer key) and
  `judge/data/todomvc-probe/` (20 rows plus a v0.9 PRD snapshot).
- Invariants: a mutation keeps its base case's `requirement_ids`; the probe uses one PRD snapshot and
  never edits it; the labeler answers pass/fail before the key is revealed; the probe's rates are
  reported apart from the designer-run sets.

## Method

Dimensions, three to start: **failure mode** (`wrong_actions`, `wrong_assertion_to_requirement`,
`case_assertion`, `prd_gap`, `incomplete_journey`), **layer** (action or expected result; preconditions
excluded because the judge does not audit them), and **granularity** (token, step, whole case).
Twenty tuples were hand-written from basis cases in the `todomvc-v07` run, then applied as exact text
edits so the rest of each case stays identical to the designer's output.

The review file lists P01–P20 in shuffled order with the intended mode removed. The key lives in a
separate file. The labeler answered "does this case verify its claimed requirement?" and the intended
modes were compared afterwards.

## Results

15 fail / 5 pass after adjudication. Prompt `8835420e`, `kimi-k2.7-code`, three runs.

| run | caught | false alarms |
| --- | --- | --- |
| `todomvc-probe-run1` | 15/15 | 1/5 |
| `todomvc-probe-run2` | 15/15 | 1/5 |
| `todomvc-probe-run3` | 14/15 | 1/5 |
| majority | 15/15 | 0/5 |

Majority `fail_recall` 1.00 [0.80, 1.00], `pass_specificity` 1.00 [0.57, 1.00]. 16 of 20 claims had
the same verdict in all three runs; the flips were the three sibling-counter assertions and the SPA
assertion, one per run.

## Findings

- The judge catches all three `incomplete_journey` probes with the reasoning "does not fully verify
  the claimed requirement". That is stricter than the prompt's fourth rule as written ("never
  asserts a result"), and the behaviour is worth keeping.
- Two probes were adjudicated after seeing the intended modes. `P05` claimed `FR-08` but performed
  `FR-23`'s journey without needing it, so the extra journey is scope creep, not a produced result.
  `P12` asserted that the page does not reload, which is an implementation property, not a result a
  step produces. Both were changed from pass to fail on that reasoning.
- Three probes the first pass called defects were accepted by the human (`P07`, `P10`, `P11`): an
  assertion on the counter that the case's own action produces is R1-legal even though `FR-TODO-14`
  owns the text. `P08` was the same class and was relabeled pass.
- The probe forced one PRD correction: `FR-TODO-17` carried "no item in edit mode", which is the
  spec's separate rule and now lives in `FR-TODO-27` (v0.9).

## Limits

- The labeler saw the tuple table before labeling, so the pass/fail answers are not blind; recall may
  be optimistic.
- n=15: the Wilson lower bound is 0.80. The five passes are accepted mutations, not natural cases.
- The verdicts move between runs; one error per run is the noise floor, and only the majority is
  usable.

## Files

- `.scratch/designer-evals/probes/todomvc-probe-1.md` — the 20 cases with the human labels.
- `.scratch/designer-evals/probes/todomvc-probe-1.key.json` — probe → requirement → intended mode.
- `evals/designer/judge/data/todomvc-probe/` — `prd.md` (v0.9) and `claims.jsonl` (20 rows).

## Comments

Opened 2026-11-11. The judge had only been measured on pass-only sets; this is the first recall
number. Reuse the method for the next PRD rather than adding more probes to this one.
