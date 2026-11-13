# 11: Add a third PRD (RealWorld / Conduit)

**What to build:** A third PRD derived from the public RealWorld specification, then one designer
run, human labels, a judge dataset, and three judge runs. This PRD exists to test the eval's rules
on a document with authentication, server state and ownership rules — three things TodoMVC cannot
express — and it is the first PRD whose journeys end in a server-returned error. The numbers stay
separate from the other PRDs; this document never enters the production pipeline.

**Blocked by:** Nothing. Ticket 09 finished the second PRD and its sets.

**Status:** ready-for-agent

**Shape:**
- Types: none. `DesignOutput`, `Case` and `LabeledClaim` keep their shape.
- Boundary: `.scratch/realworld/prd.md` (not `prd/`, which would trigger `plan.yml`), the run under
  `evals/designer/runs/`, and its dataset under `evals/designer/judge/data/realworld/`.
- Invariants: the source is pinned by commit; every requirement cites its origin — a pinned file, or a
  dated live-demo observation recorded in §9 — and adds no other behaviour; anything else the source
  leaves undefined becomes a §11 non-goal, not a requirement; the PRD is frozen once the first judge
  run starts; the dataset never mixes rows from another PRD.

## Source

`realworld-apps/realworld` @ `25588846c314b15a5e427ffe816e6b4af7be68c7` (2026-11-02), MIT.

| artifact | role |
| --- | --- |
| `docs/.../implementation-creation/features.md` | the seven features; the requirement skeleton and the scope line |
| `docs/.../specifications/frontend/routing.md` | pages and URLs; the journey entry points |
| `docs/.../specifications/frontend/templates.md` | the DOM, including the `error-messages` block; exact control labels and text an assertion needs |
| `docs/.../specifications/backend/error-handling.md` | the validation messages and status codes a failure path asserts |
| `https://demo.realworld.show` | live reference, for reviewing whether the PRD is faithful |

The E2E suite (`specs/e2e/`) is **not** a source for this ticket; see the decisions below.

## Decisions this ticket encodes

- **Scope A+:** the seven features in `features.md`, including the settings-page work that list
  names (`CRU- users`, and the logout button), plus the failure paths the source states. A journey
  that only `routing.md` adds and no feature names is not a requirement.
- **Failure paths are requirements only where the source states them.** The validation messages
  (`can't be blank`, `is invalid`, `has already been taken`) and the `error-messages` block are in
  the source, so a failed sign-in or a rejected registration can be a requirement without inventing
  anything. Behaviour the source does not state stays a §11 non-goal.
- **The E2E suite is not an oracle.** Do not read `specs/e2e/` while writing or reviewing the PRD.
  Using it would import the implementation's judgement into a document that is supposed to be
  held out from it.
- **Undefined behaviour goes to §11 as a non-goal.** Password rules, session expiry, page size, tag
  normalisation, whitespace handling and similar silent points are recorded as non-goals. The
  designer will list them under `open_questions`; the skill forbids turning one into a case
  (`SKILL.md`: "Anything the PRD leaves undefined … is **not** a case"; "Never turn an open question
  into a case").
- **A journey left out of the PRD produces nothing to measure.** It yields no case, so no claim and
  no label. It is a coverage hole, not a `prd_gap` sample: `prd_gap` needs a case that claims a
  requirement and a journey that needs an unstated behaviour.
- **The three list sources are three requirements.** Global, Your Feed and by Tag share one widget
  but not one precondition: Your Feed needs a signed-in user who follows at least one author, and a
  tag list needs an article carrying that tag. Merging them would leave two of the three sources as
  implicit assumptions inside whichever case got written.
- **Favorite/unfavorite is one requirement.** It is one rule with two directions, the same shape as
  TodoMVC's mark-all toggle.
- **Requirement ids are `FR-RW-NN`.**
- **Derivation, not extraction.** The specification is not ours, but the cut is. The PRD header says
  so, the way the TodoMVC header does.

## Tasks

- [ ] Write `.scratch/realworld/prd.md` v0.1 with the extraction rules in the header, a §9
      traceability table (requirement → source file), a §10 dropped list, and §11 non-goals.
- [ ] Cut by the branch rule: one requirement = one logic under test; a branch from a shared state
      gets its own requirement; no acceptance-criteria layer.
- [ ] Review the cut before any run. Check that no requirement states behaviour absent from its cited
      origin (a pinned file, or a dated observation in §9), and that every stated validation message
      copied into an assertion matches `error-handling.md` exactly.
- [ ] Freeze the PRD and record its `sha256` and line count in a dated comment.
- [ ] Run the designer once (paid) with an explicit `--run-id`.
- [ ] Gate before labeling: one case per requirement (or an allowed extra boundary case), no
      multi-requirement case, no duplicate, no invented ids.
- [ ] Label every claim in Phoenix: `claim_alignment`, plus `claim_failure_mode` and
      `claim_reason` on failures.
- [ ] Build `judge/data/realworld/` with `build_claims.py`, review the rows, and commit them.
- [ ] Run the judge three times (paid) and report `pass_specificity`, `fail_recall`, the confusion
      counts, the three-run agreement, and the Wilson intervals, separately from the other sets.

## Out of scope

- `specs/e2e/` as a source, an oracle or a check.
- Details that no feature names, such as the active-page CSS class and the home page's tag cloud.
- Mutation probes on this PRD. The probe method is reusable, but it is its own ticket.
- `prd/realworld.md` and the production pipeline.
- Automating RealWorld with Playwright.
- Changing the judge prompt before the first run on this PRD.

## Paid actions

- One designer call.
- Number of claims × 3 judge runs.
- Human labeling of every claim.

Confirm the budget before the first designer call.

## Risks

- The failure-path requirements copy English messages exactly; a one-word drift makes the case's
  assertion an invention, and the judge will fail it for the wrong reason.
- The live demo can drift from the specification. Grounding is not part of this ticket.
- Scope A+ is wider than the first estimate: it landed at 25 requirements after the two live-demo
  observations, so the run, the labeling and the judge calls all take longer than a happy-path cut.
- The three list requirements need seeded data the happy path does not: at least one followed author
  for Your Feed, at least one tagged article for a tag list. The cases must say so in `preconditions`,
  not in step 1.
- The specification is silent in more places than TodoMVC's; §11 may get long, and a labeler may read
  a gap as reasonable.
- The dataset is a third PRD, still short of the 5–6 a by-PRD split needs.

## Flow

```text
pin source @ 2558884
  │
  ▼
PRD v0.1 (scope A+, §9/§10/§11)
  │
  ▼
review -> freeze (sha256)
  │
  ▼
designer x1 -> label claims -> dataset -> judge x3
```

## Comments

Opened 2026-11-12 from the session that surveyed candidates. RealWorld was chosen over Restful Booker
Platform, Sauce Demo and Linkding because it is the only candidate with a public behavioural
specification, a live demo, a permissive licence, and a size that fits the eval.

Decisions taken by the human: scope A+, no E2E oracle, undefined behaviour as non-goals, ids
`FR-RW-NN`.

Ticket 09's "RealWorld's demo is gone (404)" is stale: that was `demo.realworld.io`. The project
moved to `demo.realworld.show`, and `api.realworld.show` is live.

An earlier draft of this ticket said a designer that fills an undefined behaviour produces a
`prd_gap` sample, and that is wrong twice over: the skill forbids the case, and a journey with no
requirement has no claim to label. It also put the settings page out of scope, which contradicts
`features.md` ("CRU- users (sign up & settings page)"), so the settings-page journeys are in scope.

2026-11-12: the two cut questions are settled. Global / Your Feed / by Tag are three requirements
because their preconditions differ, and favorite/unfavorite is one rule with two directions.

2026-11-13: two requirements come from observation, not the specification. On `/register` and
`/login` the submit button cannot be pressed until every field has a value; the editor does not
behave that way. The source states neither, so `FR-RW-24` and `FR-RW-25` are recorded as dated
observations in the PRD's §9, and the invariant above now allows that origin. The editor observation
is also what makes `FR-RW-10` reachable: its journey depends on pressing `Publish Article` with a
field empty.
