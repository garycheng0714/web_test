# 25: Label the designer's open questions

**What to build:** A human label for each `open_question` a designer run produces, so "finding what
the PRD left out" becomes a number instead of a side note. One run's questions are labeled, counted
by kind, and reported beside that run's other metrics.

**Blocked by:** Nothing. There are already three runs with questions to label (`realworld-v08` has 9,
the v0.6 run had 16, the todomvc runs had 11).

**Status:** needs-triage

**Shape:**
- Types: none. `DesignOutput.open_questions` stays a `list[str]`; the labels live beside the run.
- Boundary: a review file per run under `.scratch/designer-evals/probes/`-style scratch, or a new
  unit kind if the storage question below is answered that way. No Phoenix annotation: an open
  question has no span.
- Invariants: the labels never enter a claim metric (`fail_recall`, `pass_specificity`, coverage);
  they are reported per run and never pooled with another run; the designer's text is not edited.

## Why

The designer has exactly two outputs: `cases` and `open_questions`. Only the cases are measured. The
question count alone cannot be read in any direction:

| count | could mean |
| --- | --- |
| many questions | the PRD is thin — good discovery, PRD needs work |
| many questions | the designer did not read the PRD — a designer defect |
| many questions | some are not product behaviour at all (test data, environment) — noise |

The skill already constrains the third case ("an open question must be about the product's behaviour —
never about test data, the test environment, or the test process"), but nothing checks it.

A label turns the count into a signal with two uses: it measures the designer's discovery, and it
produces a list of real PRD gaps to close.

## Label vocabulary

| kind | meaning | action |
| --- | --- | --- |
| `real_gap` | the PRD does not state this behaviour | add a requirement, or record it in §11 |
| `already_stated` | the PRD states it; the designer missed it | designer defect, same family as `incomplete_journey` |
| `not_a_question` | not product behaviour | drop; the skill forbids it |

## Open question

**Where do the labels live?** Three candidates, cheapest first:

1. A review file per run (`real_world-v08.open-questions.md`), like the mutation probes. No schema
   change; manual; not queryable.
2. A third `unit` kind (`OPEN_QUESTION`) so the labels land in `units.json` and could be exported. The
   unit is span-based, so this needs a span per question or a different container.
3. A column on the run's `run.json`. Small, but labels are human edits, and `run.json` is generated.

Decide before building; option 1 is enough to test whether the metric is worth keeping.

## Tasks

- [ ] Decide the storage.
- [ ] Write the kinds into the review file with one example each from an existing run.
- [ ] Label the 9 questions of `realworld-v08` blind (before reading this ticket's reasons).
- [ ] Report `real_gap` / `already_stated` / `not_a_question` counts beside that run's metrics.
- [ ] For every `real_gap`, say whether it belongs in a requirement or in §11.
- [ ] Keep the eval suite green; no model calls are needed.

## Out of scope

- Judging the questions with an LLM. The judge scores cases; a second judge for questions is a
  different tool, and the sample is tiny.
- Feeding the labels back into the designer (a prompt or skill change).
- Pooling counts across PRDs as a quality score. Different PRDs have different amounts of silence.

## Risks

- Labeling a question requires knowing the PRD well; a careless pass will call a real gap
  `already_stated`.
- If most labels come back `already_stated`, the finding is about the designer's reading, not the PRD,
  and the metric will be uncomfortable rather than useful.
- Nine to sixteen labels per run is cheap now; it becomes a chore if every run is labeled. Label only
  when the run's numbers are being reported.

## Flow

```text
designer run ──► open_questions (9)
                     │
                     ▼
              human labels (real_gap / already_stated / not_a_question)
                     │
                     ├─► counts beside the run's metrics
                     └─► real gaps ──► requirement or §11
```

## Comments

Opened 2026-11-19 from the discussion about whether the eval can still measure the designer once the
PRD gets complete. The conclusion was that completeness moves the designer's room to fail from
"discovery" to "discipline", and that discovery currently has no metric at all — `open_questions` is
the only channel and nothing reads it. The storage decision is deliberately left open.
