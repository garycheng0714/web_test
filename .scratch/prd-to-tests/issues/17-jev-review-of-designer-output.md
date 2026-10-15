# 17: Verify the PRD→TestCase flow with Jev

**What to build:** An advisory Jev review of the designer's output. Given the PRD text and the
`DesignOutput` (cases + open questions), batch typed Jev questions (`noul`/`choice`) to flag:
ungrounded cases, duplicates, uncovered requirements (baseline), and — optionally — boundary-policy
violations and invalid open questions. Jev is a cross-check; it never generates, renders, or
authorises, and the designer stays the source.

**Blocked by:** 16 Right-size the designer's case generation (the grounded/open-question split it
verifies).

**Category:** enhancement

**Status:** needs-triage

- [ ] A batched Jev request built from the PRD + `DesignOutput.cases` + `open_questions`
- [ ] Baseline checks: per-requirement coverage (`noul`), per-case groundedness (`noul`), per-pair
      dedup (`noul`)
- [ ] Optional checks: boundary-policy compliance, open-question validity (`noul` + `choice`),
      traceability (`choice`)
- [ ] Runs against the PRD→TestCase flow (a script or a step the plan stage can call) via
      `jev-decide decide --provider typesafe`
- [ ] Only flags; it does not block, edit, or replace the designer

## Comments

Jev (`.opencode/skills/jev*`) returns typed judgments (`noul` = yes/no probability, `choice`, `score`)
and is advisory — it "does not browse, generate prose, or remember". It fits the **judgment
checkpoints** of the flow, not generation or rendering.

Where it maps to the current flow (`web_test/planning/designer.py` → `DesignOutput(cases,
open_questions)`; policy in the `qa-test-case-generation` skill):

| Step | Jev question | Type | Catches |
| --- | --- | --- | --- |
| Per requirement | "Is there a grounded happy-path case covering it?" | `noul` | uncovered requirements |
| Per case | "Is this case directly supported by the PRD text, or invented?" | `noul` | ungrounded cases (the core of ticket 16) |
| Per case pair | "Do these two cases test the same behavior?" | `noul` | duplicates that restate others |
| Per boundary case | "Does the PRD state the limit this exercises, and does the happy path not already cover it?" | `noul` | grounding-observed cases, extra boundaries |
| Per open question | "Is this genuinely undefined by the PRD (or already stated/contradicted)?" | `noul` + `choice` | fake or missing open questions |
| Per message | select the exact verbatim string from candidates | `choice` | paraphrased messages (span selection) |

Shape (one batched request; independent questions over shared state):

```jsonc
{
  "model": "typesafe/jev-1.13",
  "state": { "prd": "...", "cases": [ /* ... */ ], "open_questions": [ /* ... */ ] },
  "questions": {
    "cov_FR-ACC-01":       { "type": "noul",   "instructions": "Is at least one supplied case a grounded happy path for FR-ACC-01?" },
    "grounded_case_1":     { "type": "noul",   "instructions": "Does the PRD text directly support case 1 as stated?" },
    "dup_1_2":             { "type": "noul",   "instructions": "Do cases 1 and 2 test the same behavior per the dedup rule?" },
    "oq_1_valid":          { "type": "noul",   "instructions": "Is open question 1 genuinely undefined by the PRD?" }
  }
}
```

Run: `python3 .opencode/skills/jev/scripts/jev.py decide request.json --provider typesafe`
(or `jev-decide decide request.json --provider typesafe`); `TYPESAFE_API_KEY` is required and present
locally. Read the answers, not just the exit code (`0` selected, `2` needs review, `1` error). Use
`WEB_TEST_USAGE`-style logging for the host run's cost, and log the Jev request/response as a review
artifact.

Open (decide before implementing):

- **Scope** — baseline three (coverage, groundedness, dedup) only, or also boundary-policy and
  open-question validity? Recommendation: baseline first.
- **One-off vs reusable** — a throwaway review experiment, or a step the plan stage calls (a small
  module + tests, host-side)?
- **CJK** — the PRD and cases may be Chinese/English mixed; Jev's docs say English is best supported.
  Test as-is, or send an English translation for the Jev request?
- **Where the flags go** — print to stderr, a review file next to the artifact, or a PR comment?

Boundaries: Jev supplies judgments, not facts; it is not an authorization or security gate. Counts and
arithmetic (e.g. coverage tallies) stay in code. It must not generate cases, render the artifact, or
decide "what the requirement should be" — it only checks what the supplied text supports.

## Research — Jev experiment on the `register-login` artifact (2026-10-15)

Method: built batched requests from the PRD text and the `DesignOutput` / rendered artifact
(`test-case/test-case-register-login.md`, 7 cases, 11 open questions); ran
`jev-decide decide ... --provider typesafe` (model `jev-1.13.0`); read the answers and the exit code.

Summary:

| Check | Jev question | Signal this run | Verdict |
| --- | --- | --- | --- |
| Per-requirement coverage | `noul` × 6 | 6/6, all `p = 0.99` | Drop from Jev → do as a code count |
| Groundedness | `noul` per case × 7 | 7/7 grounded, `p` 0.93–0.97 | **Add** (core) |
| Dedup | pairwise `noul` × 21 | 0 duplicate pairs, `P(dup) ≤ 0.10` | **Add** |
| Boundary-policy | `noul` per case × 7 | Vacuous — no boundary/UI/validation cases; 7/7 still in policy (`p` 0.89–0.93) | Defer |
| Open-question validity | `noul` + `choice` × 11 | 11/11 valid (`p` 0.56–0.94); all `missing_rule`; **#11 flagged at `p = 0.56` (exit 2)** — a test-data/process question, not a product gap | Advisory + fix the class in the skill |

Results:

- **Per-requirement coverage** (`noul` × 6): 6/6 covered, every `p = 0.99`. Near-zero signal — the
  policy keeps it trivially true.
- **Groundedness** (`noul` per case × 7): 7/7 grounded (`p` 0.93–0.97). Clean on the right-sized
  output; this is the check that would catch a return to inferred cases.
- **Dedup** (pairwise `noul` × 21): 0 duplicate pairs (`P(dup) ≤ 0.10`). Matches the manual read.
- **Boundary-policy** (`noul` per case): the run has **no boundary/UI/validation cases** (all
  Functional/Workflow/Negative), so the check is **vacuous**; every case is nonetheless in policy
  (`p` 0.89–0.93).
- **Open-question validity** (`noul` + `choice` × 11): all 11 judged genuinely undefined
  (`p` 0.56–0.94), all classified `missing_rule` (`p` 0.70–0.99). **One flagged** — OQ #11
  ("where does the pre-existing test account come from?") at `p = 0.56`, exit `2`: it is a
  **test-data/process** question, not a product-behaviour gap (and it cites `PRD §9#4`, which does
  discuss the topic), i.e. an off-type open question.
- **Cost**: two batches, ~6.8k/0.7k and ~8.6k/0.9k tokens; `exit 2` fired on the low-confidence item
  (default `min_probability` 0.8). CJK (Chinese PRD + English cases) judged with high confidence, so
  the CJK caveat is not acute for these checks.

Conclusion (recommendation):

- **Add**: **groundedness** and **dedup** — the two checks that key off the failure mode this repo
  actually had (inferred cases, restated cases), as an on-demand advisory review.
- **Do not use Jev for coverage** — always ~0.99; make it a code count instead ("does each FR have a
  grounded happy-path case?").
- **Defer** the boundary-policy check — vacuous on healthy output; groundedness/dedup already catch
  the over-generation it would flag.
- **Open-question validity**: keep as advisory (it caught a real off-type question), but fix the class
  at the source: add a skill rule that an `open_question` must be a product-behaviour gap, never a
  test-data/process question. Then Jev's `oq` check is a backstop, not the primary defence.

So the "baseline three" is really **two**: groundedness + dedup. Coverage moves to code; the rest is
deferred or handled in the skill.

