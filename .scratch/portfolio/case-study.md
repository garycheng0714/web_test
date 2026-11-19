# Portfolio case study: an eval for a PRD-to-test-case generator

Target role: **AI / eval engineer**. The product (an agent that turns a PRD into Playwright tests) is
the context; the star is the evaluation and the fact that the evaluation itself was evaluated.

## The one-sentence pitch

> I built a generator, then built a human-labeled evaluation for it, then found and fixed three
> defects in the evaluator — including one that was a defect in the unit of evaluation, not the
> model.

## Strongest assets, in the order this role reads them

| What the role wants | What this repo has | Where |
| --- | --- | --- |
| A unit and a ground truth | `claim = (case, requirement)`; human labels are truth; Phoenix is a UI, not storage | `evals/designer/spec.md`, `judge/data/README.md` |
| Judge validation | two mutation probes, 17 and 15 constructed defects; recall 1.00 / 0.93 | `.scratch/designer-evals/probes/`, `judge/data/*-probe/` |
| Reproducible iteration | prompt = sha256; one variable per change; old numbers tagged with their version; each judge run carries its inputs | `evals/designer/designer_eval/judge.py`, `judge/runs/<id>/inputs/` |
| Failure taxonomy | `wrong_actions`, `prd_gap`, `case_assertion`, `wrong_assertion_to_requirement`, `incomplete_journey` | `spec.md` |
| Engineering | uv, ruff, basedpyright (tests included), import contracts, CI, coverage gates | `pyproject.toml`, `.github/workflows/` |

The senior signal is not the generator. It is that the **unit changed**: the judge was failing cases
partly because "requirement = one journey with results" was the wrong unit. The fix was "rule +
journeys", with a parser change, a prompt change, and a PRD change.

## Numbers to quote (and how to qualify them)

Prompt history, same claim sets:

| prompt | rule | designer-set specificity | probe recall |
| --- | --- | --- | --- |
| `8835420e` | strict text | 0.77 | 0.94 |
| `67265b54` | strict + null for non-assertions | 0.80 | n/a |
| `cbbb6990` | ordinary consequences | 0.93 | 0.94 |
| `6a369dd2` | rule + journeys | 1.00 (v0.8) | 0.88 |
| `c1f862a4` | + visibility of the assertion | 1.00 (v0.8) | 1.00 |

Sets: `automationexercise` 27 claims, `todomvc-v08` 28, `realworld-v08` 33; probes 20 rows each
(17 / 15 defects).

Qualifications, say them before they are asked:

- **dev only.** All three PRDs were used while tuning the prompt. There is no held-out PRD yet.
- **small n.** 27–33 claims; Wilson intervals are wide.
- **1/3 flips.** The judge's verdict moves between runs on roughly one claim in three; that is why
  runs are three and the majority is reported.
- **negative samples are constructed.** The probes are exact-text mutations, not natural designer
  output; the 5 passes in the TodoMVC probe are mutations a human accepted.

## The gap that matters: held-out

`held-out` is the question an eval engineer asks first. The honest answer is "not yet", plus a plan:

```text
1 new PRD (15-20 requirements is enough)
designer x1 -> human labels -> same prompt -> report specificity
recall comes from the existing probes
```

This turns "dev only" into "has a held-out estimate" and is the single most valuable addition.

## Three defects in the evaluator (the interview story)

| Symptom | Diagnosis | Fix |
| --- | --- | --- |
| the judge failed steps that only assert "the field shows what I typed" | `grounded` had no third value; the rubric said these are not assertions, the schema forced true/false | `grounded: bool \| None` |
| the judge accepted an assertion about a page the case never opened | "global state" was read as "the relationship exists" | rule 3: the assertion must be visible on a page the case opens |
| a case that performed one of two journeys looked incomplete | the requirement unit was a journey with several results | unit is now rule + journeys; `parse_requirements` and the prompt carry them separately |

Each fix came with a measurement, and each measurement is attached to a prompt hash.

## Case study outline (1-2 pages)

1. **Problem** — a generator whose mistakes nobody measured.
2. **Unit** — claim = (case, requirement); why not a case.
3. **Ground truth** — human labels, three columns, Phoenix is not storage.
4. **Judge** — one criterion, four fail rules, whole PRD + case as input.
5. **Validating the judge** — two probes; recall 1.00 / 0.93; what a probe can and cannot show.
6. **Three defects found** — schema, prompt, unit (the table above).
7. **Result** — the prompt table; specificity and recall moving in opposite directions at
   `6a369dd2`, then both at `c1f862a4`.
8. **Limits** — dev only, small n, flips, constructed negatives.
9. **Next** — held-out PRD, gate policy (three runs, threshold, appeal), open_question labels.

## Demo script (3-5 minutes)

```text
1. designer run dir: design.json, units.json, run.json, prd.md
2. Phoenix: requirement and claim spans, human labels
3. judge report: one disagreement, expanded critique, inputs/ beside it
4. probe: P18 ("asserts a page it never opens") and why it was missed
5. prompt table: one slide
```

## Before sharing

- `README.md` does not mention the evaluation at all. Add an "Evaluation" section linking
  `evals/designer/spec.md`, or the reviewer will only see the product.
- Judge token usage is not recorded (`ticket 07`, open item). "What does one evaluation cost?" is a
  guaranteed question; today the answer is an estimate.
- Fix the stale line in `evals/designer/README.md` ("one PRD only") — there are three.

## Five questions to be able to answer unaided

1. Why is a claim `(case, requirement)` and not a case?
2. Why construct a probe instead of waiting for the designer to fail naturally?
3. Why is specificity 1.00 not "the judge is accurate"?
4. How do you know whether a change moved the prompt, the PRD, or the data?
5. If this had to gate merges tomorrow, what comes first and what comes later?

## Meta: this work was AI-assisted

The risk in an interview is that the artifacts look better than the candidate's understanding. Own
the decisions: be able to derive the unit, the three defects and the trade-offs without the notes.
The ticket ledger is evidence of the decision process, not a substitute for it.
