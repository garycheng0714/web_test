# Eval system — audit and ticket map

**Status:** ready-for-agent (tickets 01–10 published; 02–04 are human work)
**Source:** `eval-audit` applied to the current pipeline, 2026-10-25.
**Scope:** designer, Jev verifier, automation, the human Gate, and CI.

## Why

The pipeline can produce test cases and Playwright tests, but it cannot answer whether a
change to a prompt, skill, or model made the output better. Only the verifier has an eval,
and that eval is a six-case regression fixture with no human labels. Every model/prompt
decision today is made from a single run or a hand-written comparison log.

## Findings, ordered by impact

| # | Finding | Area | Severity | Ticket |
| --- | --- | --- | --- | --- |
| 1 | Jev is unvalidated against human labels; false PASS rate is unknown | Judge validation | Critical | 04, 05 |
| 2 | The fixture is both dev and test; no held-out set | Judge validation | Critical | 04 |
| 3 | No systematic error analysis for designer or automation | Error analysis | High | 02 |
| 4 | The eval is a manual CLI; CI never runs it | Pipeline hygiene | High | 09 |
| 5 | No designer eval | Evaluator design | High | 08 |
| 6 | No automation eval; green/repair/cost exist only in manual logs | Evaluator design | High | 07 |
| 7 | 6 cases and 1 PRD are far below any validation threshold | Labeled data | High | 04 |
| 8 | Bands (0.8 / 0.5) are defaults, never calibrated | Judge validation | Medium | 05, 06 |
| 9 | AC alignment is a case-level holistic judgment | Evaluator design | Medium | 03 |
| 10 | The four-class verdict is a gate, but there is no per-class metric | Evaluator design | Medium | 05 |
| 11 | Human adjudications are written to a check summary and then lost | Human review | Medium | 01 |
| 12 | A reviewer cannot see the PRD path or the designer's open questions in the summary | Human review | Medium | 10 |
| 13 | Requirement coverage is computable but unchecked | Evaluator design | Medium | 08 |
| 14 | Changing a skill or instruction has no re-validation step | Pipeline hygiene | Medium | 07, 08, 09 |
| 15 | One domain only (register/login) | Labeled data | Low | deferred |

## What already works

- The reviewer is the domain expert (the builder), not an outsourced annotator.
- The Gate is a PR merge; the verification check is required; `FAIL` is not overridable;
  adjudication is bound to the head SHA.
- Deterministic checks exist where they should: structure checks, generated-test quality
  rules, front-matter parsing, resolution.
- Jev is pinned (`jev-1.13.0`), and the binding records the model, question-set version,
  check-set version, bands, and both digests.
- Kill criteria are pre-registered.
- No similarity metric (ROUGE, BERTScore, cosine) is used as a primary evaluator.
- Reviewer data is rendered as markdown tables, not raw JSON.

## Not ticketed

- **Second domain (finding 15).** Deferred until the first designer and verifier datasets
  are stable; adding a domain before the harness works only adds maintenance.
- **Green-run evidence (low).** A green automation run already carries a run report in the
  PR body; a separate artifact is not worth the noise yet.
- **A dashboard.** The reports are markdown; a dashboard is a later decision.

## Ticket map

| Ticket | Delivers | Blocked by |
| --- | --- | --- |
| 01 | Durable human adjudications for calibration | none |
| 02 | An observed failure taxonomy for both stages | none |
| 03 | A decision on AC alignment granularity | none |
| 04 | A labeled verifier set with train/dev/test | 03 |
| 05 | TPR/TNR, false PASS, confusion matrix, CI | 04 |
| 06 | Calibrated bands | 05 |
| 07 | A repeatable automation eval with paired comparison | none |
| 08 | A deterministic designer eval | 07 |
| 09 | Eval in CI with retained history | 05, 07, 08 |
| 10 | PRD path and open questions in the summary | none |

## How to read the findings

The two critical findings are the same problem from two sides: without human labels,
there is no way to know whether Jev's verdicts are right, and without a held-out set there
is no way to know whether the numbers survive the next change. Everything else is
either a missing stage eval or a missing piece of comparability.

The first usable numbers do not require the critical path: ticket 07's automation eval
and ticket 08's designer eval are deterministic, need no labels, and answer "did this
change make the output better?" for the two most expensive stages. The verifier
calibration (04–06) makes the semantic numbers trustworthy and is the longer path.
