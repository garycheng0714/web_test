# 23: Give the judge a "not an assertion" verdict per step

**What to build:** `StepCheck.grounded` becomes `bool | None`. `None` means the step's
`expected_result` is only one of the instructions' non-assertions — setup, page or context, form-field
mechanics, element presence, a "no error" clause — so there is nothing to ground. Only `false` fails
the case. The prompt says so in the step-audit paragraph, in fail rule 2 and in the non-assertion
list.

**Blocked by:** Nothing.

**Status:** ready-for-agent

**Shape:**
- Types: `StepCheck.grounded: bool | None`. `JudgeOutput` and `JudgeRecord.checks` keep their shape
  (`checks` is `list[dict[str, object]]`, so the JSONL gains a null, not a field).
- Boundary: the judge's structured output and, through it, `judgements.jsonl`.
- Invariants: `true` = grounded; `false` = ungrounded and fails the case; `null` = not an assertion
  and never fails the case; the model never uses `null` for an assertion it could not decide (that is
  `false`).

## Why

Three of the seven majority failures on `realworld` are the judge contradicting its own rubric. The
prompt ends with "these are not assertions: … page or context assertions, form-field input mechanics,
element presence, and 'no error' clauses", but the step audit says "if any check is not grounded, the
result is fail", and `grounded` had only two values.

```text
case-26 -> FR-RW-19   step 1: "text appears in the input box"
                      judge note: "input mechanics/setup state are not assertions"
                      judge value: grounded = false          -> case fails

case-14 -> FR-RW-09   steps 1-2: "button enabled", "leaves the editor", "no error"
case-15 -> FR-RW-10   step 1: "Publish Article can still be pressed"
```

The model knew the rule and had no way to record it. A two-valued field forces a choice between
"grounded" and "failed" for something that is neither.

## Tasks

- [ ] Change `StepCheck.grounded` to `bool | None` in `designer_eval/judge.py`.
- [ ] Rewrite the step-audit paragraph: true/false/null, and "if any check is false, the result is
      fail".
- [ ] Rewrite fail rule 2 so it applies to "an expected_result that is an assertion".
- [ ] Add "a step whose expected_result is only one of these gets `grounded: null`" to the
      non-assertion paragraph.
- [ ] Add a test that a null-grounded check validates and survives `model_dump`.
- [ ] Keep the suite, `basedpyright` and `ruff` green.
- [ ] Re-run the judge on `realworld` three times (paid) and compare with the v1 prompt's 0.77.

## Out of scope

- The requirement shape that made the other three failures: `FR-RW-14`, `FR-RW-16` and `FR-RW-21`
  state a second direction that needs a different actor or state, which one case cannot assert.
  Splitting those requirements is a PRD decision with its own designer re-run.
- Any change to the human labels.
- Re-baselining the other datasets. The prompt hash changes, so their numbers become a previous
  version; record the hash beside every rate rather than re-running them here.

## Paid actions

- `realworld` × 3 = 90 judge calls for the comparison.

## Result (2026-11-15)

| run | fail | `pass_specificity` |
| --- | --- | --- |
| `realworld-run1-v2` | 6 | 0.80 [0.63, 0.90] |
| `realworld-run2-v2` | 5 | 0.83 [0.66, 0.93] |
| `realworld-run3-v2` | 6 | 0.80 [0.63, 0.90] |
| majority | 6 | **0.80** [0.63, 0.90] |

Prompt `67265b54`, 90 calls. The change did what it was written to do: `case-15` (the editor button's
enabled state) and `case-26` (text in the input box) now pass, and `case-14`'s button objection is
gone. `null` is being used; no critique claims a non-assertion is ungrounded any more.

The headline moved 0.77 → 0.80, not the predicted 0.87, because the remaining failures are a
different cause. Six majority failures:

- **3 requirement shape** — `FR-RW-27` (two pages), `FR-RW-14` and `FR-RW-21` (two directions that need
  different actors). The case covers one result, defers the other, and the judge cannot see the sibling
  case.
- **3 over-assertions** — `FR-RW-07` "the settings were saved", `FR-RW-09` "the screen leaves the
  editor" (which §11 says is unspecified), `FR-RW-28` "the account was not created".

So 0.80 is a cleaner number than 0.77 but still not a clean judge estimate: the requirement-shape
family is a PRD decision, not a judge defect. If those three requirements were split by page/actor,
the same prompt would measure about 0.90.

Keep the change. The requirement-shape question is its own ticket.

## Risks

- The prompt hash changes from `8835420e…` to `67265b54…`. Rates measured with the old hash are not
  directly comparable; every report that cites 0.77 must name its prompt.
- A model can still misuse `null` for a genuinely undecidable assertion. The test covers the schema,
  not the model; only a run shows whether the prompt is obeyed.
- If the fix works, the RealWorld specificity should rise from 0.77 to at least 0.87 without touching
  the labels. If it does not, the cause is not the schema and the change should be reverted rather
  than layered on.

## Flow

```text
schema: bool          ->  bool | None
prompt: 2 values      ->  true / false / null
                       │
                       ▼
                  realworld x3 (paid)
                       │
                       ▼
             pass_specificity vs 0.77
```
