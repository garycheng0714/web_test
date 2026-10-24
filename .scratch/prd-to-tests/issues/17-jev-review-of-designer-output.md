# 17: Verify the PRD→TestCase flow with Jev

**What to build:** An advisory Jev review of the designer's output. Given the PRD text and the
`DesignOutput` (cases + open questions), batch typed Jev questions (`noul`/`choice`) to flag:
ungrounded cases, duplicates, uncovered requirements (baseline), and — optionally — boundary-policy
violations and invalid open questions. Jev is a cross-check; it never generates, renders, or
authorises, and the designer stays the source.

**Blocked by:** 16 Right-size the designer's case generation (the grounded/open-question split it
verifies).

**Category:** enhancement

**Status:** ready-for-human (done; implemented)

- [x] A batched Jev request built from the PRD + `DesignOutput.cases` + `open_questions`
- [x] Baseline checks: per-requirement coverage (`noul`), per-case groundedness (`noul`), per-pair
      dedup (`noul`)
- [x] Optional checks: boundary-policy compliance, open-question validity (`noul` + `choice`),
      traceability (`choice`)
- [x] Runs against the PRD→TestCase flow (a script or a step the plan stage can call) via
      `jev-decide decide --provider typesafe`
- [x] Only flags; it does not block, edit, or replace the designer

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

**Revisited — reduced to groundedness only.** Dedup is already the skill's job (the
`qa-test-case-generation` skill has a `## Deduplication` section and a "no case that merely restates
others" rule), the two experiments returned **0 duplicates**, and it is the **O(N²)** check (7 cases →
21 questions, 30 → 435) — the most expensive, lowest-signal one. Open-question validity was dropped
too: the open questions are already listed in the PR body, and on the right-sized output the check was
mostly green with occasional low-confidence noise. **Kept: per-case groundedness** — the one check
that keys off the failure mode this repo actually had (inferred cases) and stays O(N). The review is a
regression sentinel over skill compliance; the human Gate remains the only guarantee.

## Implementation

Decisions: run **in `plan`** (in-process), a single check — **per-case groundedness** (no coverage, no
dedup, no open-question validity), appended to the **PR body**, advisory, silently skipped when
unavailable.

- `web_test/planning/review.py` — the state models (`ReviewCase`/`ReviewState`), the
  `ReviewRequest`/`Verdict` dataclasses, `build_request(prd_text, design)` (one groundedness `noul`
  per case), and `run_review(prd_text, design, *, system_one=…) -> dict[str, Verdict] | None`: it
  builds the request, calls Jev, and returns the verdicts (or `None`). Degrades to `None` on any
  exception (no key, network/SDK error, empty answers).
- `web_test/planning/review_report.py` — the **pure renderer**:
  `render_report(verdicts, design, *, threshold=0.8) -> str` (a `**Groundedness:** x/N grounded` line +
  findings + "needs review"), split from the side-effecting call so it is testable without the SDK.
  "Needs review" uses the verdict's **confidence** — a `noul` reports P(yes), so a `False` answer is
  inverted (`1 - probability`).
- **Transport: the `typesafe-sdk` directly** (not the `jev-decide` CLI). The request and answers are
  typed: `build_request(prd_text, design) -> ReviewRequest` where `state` is a Pydantic `ReviewState`
  (`prd`, `cases: list[ReviewCase]`; each case's steps flattened to an `action -> expected` line) and
  `questions` is a `Mapping[str, Noul]` of SDK question objects; answers come back as
  `Verdict(value, probability)` dataclasses. `SystemOne` is the injected seam:
  `Callable[[ReviewRequest], dict[str, Verdict]]`; the default `_typesafe_system_one` calls
  `AsyncTypeSafeClient().system_one(request.state.model_dump(), questions, model='jev-latest')` under
  `run_sync` and normalizes the typed answers (`NoulAnswer.noul`). Reads
  `TYPESAFE_API_KEY`/`TYPESAFE_BASE_URL` (default `api.typesafe.ai`); no Pydantic AI Gateway needed. The
  earlier CLI shell-out was dropped: it depended on a globally-installed `jev-decide`, parsed JSON by
  hand, and stored a temp request file. Added `typesafe-sdk` as a dependency.
- `web_test/planning/entrypoint.py` — `plan(..., reviewer: Reviewer = run_review)`; reads the PRD once,
  runs the review after the designer (`verdicts = reviewer(prd_text, design)`), renders it
  (`render_report(verdicts, design)`), and hands the text to `publish`.
- `web_test/planning/publisher.py` — `publish(..., review=None)`; appends it to the PR body via
  `plan_pr_body(prd_stem, cases, open_questions, review)` (after a `---` separator). The review is
  computed before the PR is opened, so the body carries it in the single `gh pr create` call.
- Tests: `tests/planning/test_review.py` (request shape + `run_review` returning verdicts/degrade paths
  via an injected `system_one`), `tests/planning/test_review_report.py` (report rendering incl. the
  confidence inversion), publisher body, and `plan` rendering the verdicts into the PR body.

Effect: `plan` now appends a `## Jev review (advisory)` section (per-case groundedness) to the Gate PR
body and skips it when Jev is unavailable. It never blocks. `uv run pytest`: 96 passed, 1 skipped.

**2026-10-24 — bookkeeping: done.**

The advisory Jev review lives in `web_test/planning/review/` and is appended to the plan PR body; it never blocks. Status → `ready-for-human (done; implemented)`.
