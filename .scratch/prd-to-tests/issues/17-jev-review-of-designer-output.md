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
