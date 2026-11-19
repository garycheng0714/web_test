# 26: Keep one PRD out of judge tuning

**What to build:** A fourth PRD that never takes part in a prompt or PRD change, run through the
current designer and judge once, labeled by a human, and reported on its own. It exists to answer one
question the existing three cannot: does the judge keep its specificity on a document nobody tuned it
on?

**Blocked by:** Nothing.

**Status:** needs-triage

**Shape:**
- Types: none. The dataset is a normal `judge/data/<name>/` with a frozen PRD snapshot.
- Boundary: `.scratch/<name>/prd.md`, `evals/designer/runs/<run-id>/`, `judge/data/<name>/`.
- Invariants: the PRD is frozen **before** the first judge run and never edited afterwards; no prompt
  or skill change may be motivated by its results; its rates are reported apart from the three dev
  sets; it is never pooled into their denominators.

## Why

"held-out" has been used in two senses, and only one is satisfied today.

| sense | status |
| --- | --- |
| held out from the **specification** — the PRD is a derivation, not reverse-engineered from the app | ✅ TodoMVC and RealWorld |
| held out from **judge tuning** — never used while changing a prompt or a PRD | ❌ none |

All three PRDs were read, and their failures explained, while rule 2, rule 3, the `grounded` schema
and the rule-and-journeys unit were written. The 1.00 specificity on `realworld-v08` is therefore a
dev number, not an estimate of what a new PRD would score. Ticket 03's train/dev/test task is blocked
on the same gap.

## Candidates

From the survey in ticket 11, minus the two already judged:

| candidate | live | public behavioural spec | note |
| --- | --- | --- | --- |
| Restful Booker Platform | `automationintesting.online` | API docs only; UI must be derived | different domain (date ranges, admin) |
| Sauce Demo | `saucedemo.com` | none | pure derivation from the implementation |

Pick one and write the PRD the way the others were written (extraction rules in the header, §9
traceability, §10 dropped, §11 non-goals). A PRD that is a derivation is acceptable as long as its
header says so; what matters is that it is written before any judge result is seen.

## Tasks

- [ ] Pick the candidate and write its PRD; freeze it with a `sha256` before any run.
- [ ] Run the designer once (paid) with an explicit `--run-id`.
- [ ] Gate: one case per journey, no duplicate, no invented id, every requirement claimed.
- [ ] Label every claim in Phoenix; build `judge/data/<name>/`.
- [ ] Judge ×3 with the current prompt; report `pass_specificity` and its Wilson interval.
- [ ] State plainly whether the number holds, and what a drop would mean.
- [ ] Record the result in this ticket and in the PRD's own ticket.

## Out of scope

- Using the result to change the prompt. If it drops, that is a finding, not a tuning input; a later
  prompt change needs its own held-out PRD.
- Recall. The probes already cover it; this set is pass-heavy, like the others.
- A gate. This measures the judge; it does not make a gate.
- Pooling with the three dev sets or replacing any of them.

## Paid actions

- One designer call.
- Number of claims × 3 judge calls.
- Human labeling of every claim.

At 20–25 claims this is the smallest complete loop in the eval so far.

## Risks

- One PRD with 20–25 claims gives a wide interval; it shows "not only these three", not a population
  estimate.
- The designer will keep changing; the set measures the prompt as of its run, not forever.
- A derivation-heavy PRD (Sauce Demo) tests the judge on a document we wrote, which is weaker than
  TodoMVC's public spec. Say so in the PRD header.
- If the result is poor, the temptation will be to tune and re-run — which destroys the held-out
  property. The next held-out must then be a different PRD.

## Flow

```text
pick + write PRD ──► freeze (sha256) ──► designer x1 ──► label
                                                         │
                                                         ▼
                                             judge x3, current prompt
                                                         │
                                                         ▼
                                        report specificity, apart, once
```

## Comments

Opened 2026-11-19 from the portfolio discussion: an eval engineer's first question is whether the
metric holds on a document the author has not tuned on, and today the answer is no for all three
PRDs. It also unblocks half of ticket 03's train/dev/test split (dev + test PRDs), though the split
still needs a fifth for train.
