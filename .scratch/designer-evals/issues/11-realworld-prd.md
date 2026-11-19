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
- [x] Review the cut before any run. Check that no requirement states behaviour absent from its cited
      origin (a pinned file, or a dated observation in §9), and that every stated validation message
      copied into an assertion matches `error-handling.md` exactly.
- [x] Freeze the PRD and record its `sha256` and line count in a dated comment.
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
- Scope A+ is wider than the first estimate: it landed at 28 requirements after the live-demo
  observations and the visitor rules, so the run, the labeling and the judge calls all take
  longer than a happy-path cut.
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

Same day, v0.3: `FR-RW-16` gains the "following nobody" empty state, including the copy
`Your feed is empty. Follow some users to see their articles here, or check out the Global Feed!`.
That string is not in the pinned spec either; it is the Angular implementation's `empty-feed-message`,
so the PRD now pins two implementation-level strings (this and the disabled buttons). Section 11's
empty-state row was narrowed to the other lists so the two do not contradict.

Same day, v0.4: visitor behaviour becomes its own requirements. `FR-RW-26` (the `Your Feed` tab
appears only after signing in) comes from templates.md and had only been described in §3.3. `FR-RW-27`
(a guest opening `/settings` or `/editor` is sent to `/login`) comes from the demo's route guard.
A rule that lives only in a precondition never becomes a claim, so it never gets a label or appears
in coverage; that was the reason to promote these. §11's row about a guest pressing favorite/follow
now records the demo's inconsistency (favorite → `/register`, follow → `/login`) instead of leaving
the targets unstated.

Same day, v0.5: a successful sign-in or sign-up lands on `/` (`router.navigate(['/'])`), so
`FR-RW-01` and `FR-RW-03` now say so. That is the fifth observation, and it replaces §11's old
"which page after auth" row with the case the demo does not settle: a signed-in user opening
`/login` or `/register`.

2026-11-13: the PRD is frozen at **v0.5**.

- `sha256` `0b2136094587e53d7447a6c5ac885eed5222276392d8b4dcf759c95507e7f063`, 377 lines,
  27 requirements, no acceptance criteria.
- Any later edit invalidates the comparison and belongs in a new version.
- The review was not a separate pass: the cut was checked mechanically during the session
  (`parse_requirements` reads 27, ids are contiguous and unique, every requirement cites a pinned file
  or a §9 observation, §9 covers 27/27, no acceptance criteria) and the human decided each addition in
  the conversation. Five behaviours now come from the demo rather than the spec; they are listed in
  §9 and are the first assertions that would fail against a different Conduit implementation.

2026-11-13, v0.6: `FR-RW-02` was two validation rules in one requirement — uniqueness
(`has already been taken`) and format (`is invalid`) — which breaks the PRD's own rule 2. The designer
had merged both into one case and said so in its notes, which is what exposed it. The requirement now
covers uniqueness only, and `FR-RW-28` covers format; 27 -> 28 requirements.

The PRD is frozen again at **v0.6**: `sha256`
`0cb7426742416f8ca0f69f99ce8e03d0b3364625e9093b74dffa1f3e2348009d`, 384 lines. The v0.5 freeze and
its run `realworld-v05-20261113` are superseded: that run answered a PRD that no longer exists, so it
must not be labeled, exported or compared. No labels had been made, so nothing was lost but the one
designer call.

2026-11-15: v0.6 ran as `realworld-v06-20261113`. 28 requirements, 30 cases, 30 claims, usage 39,496;
the gate passed with two extra cases (`FR-RW-16` for the followed/empty halves, `FR-RW-27` for the two
protected pages). All 30 claims are human-labeled **pass**, so the dataset is pass-only.

Judge ×3 on that set: majority 7 fail, `pass_specificity` **0.77 [0.59, 0.88]**, `fail_recall` `n/a`;
per run 0.77 / 0.80 / 0.80, 9 claims flipped at least once. The seven split into three kinds:

- **3 are the judge contradicting its own rubric** — it treated non-assertions (form mechanics, a
  button's enabled state, "no error", leaving the editor) as ungrounded assertions. Prompt `8835420e`;
  fixed by ticket 23.
- **3 are a requirement shape** — `FR-RW-14`, `FR-RW-16`, `FR-RW-21` state a second direction that
  needs a different actor or state, so one case cannot assert both and the judge sees a case that
  looks incomplete. Splitting them is a PRD decision, not made here.
- **1 is a real over-assertion** — `case-12` asserted that the settings were saved, which no
  requirement states.

So the first number on this PRD measures a prompt defect mixed with a PRD-shape question; it is not a
clean estimate of the judge. Ticket 23 is the prerequisite for reading it.

2026-11-15, second measurement after ticket 23. Same 30 claims, prompt `67265b54`, three runs:
0.80 / 0.83 / 0.80, majority **0.80 [0.63, 0.90]**. The non-assertion false alarms are gone
(`case-15`, `case-26` now pass; `case-14`'s button objection disappeared). The six remaining majority
failures are three requirement-shape disagreements (`FR-RW-14`, `FR-RW-16` in some runs, `FR-RW-21`,
`FR-RW-27` — a case covers one of two stated results and the judge cannot see the sibling case) and
three real over-assertions (`FR-RW-07` persistence, `FR-RW-09` "leaves the editor", `FR-RW-28` "account
not created"). Splitting the multi-result requirements is the next decision; it needs a designer
re-run.

2026-11-16, third measurement: the judge now accepts the ordinary consequence of a stated result
(prompt `cbbb6990`). Three runs: 0.97 / 0.87 / 0.93, majority **0.93 [0.79, 0.98]** — two failures
left. `FR-RW-07`, `FR-RW-21`, `FR-RW-27` and `FR-RW-28` pass. The two that remain are
`FR-RW-09` (blocked by this PRD's own "post-publish redirect unspecified" note, not by the judge) and
`FR-RW-14` (the author direction is never asserted; that is incompleteness, which leniency cannot
excuse). No negatives exist in this set, so the cost of the wider rule is unmeasured until a probe for
this PRD exists.

2026-11-16, the probe: `realworld-probe-1` is 20 exact-text mutations of the v0.6 cases (17 defects,
3 accepted changes). Three runs with prompt `cbbb6990`: **`fail_recall` 0.94 [0.73, 0.99]** (16 of 17),
**`pass_specificity` 1.00 [0.44, 1.00]** (3 of 3), same verdict in all three runs for 19 of 20 rows.

The one miss is `P08 -> FR-RW-19`, the weakest mutation: it adds "immediately, without a reload" to a
comment step. The judge read that as part of the stated result, which is defensible; the strict label
calls it a `prd_gap`. So the wider rule did not trade recall away: one borderline item, nothing else.

The first human pass over the probe agreed with the construction on 8 of 20; the strict reading was
adopted after adjudication (see `judge/data/README.md` and the probe key).

2026-11-18, v0.8 and the rule-and-journeys judge. The PRD promises the publish redirect and states
the five two-journey requirements as two bullets each (PR #56); the judge receives a rule and its
journeys instead of loose markdown (PR #55).

Run `realworld-v08-20261117`: 28 requirements, **33 cases** — `FR-RW-14`, `16`, `21`, `26` and `27`
each produced one case per journey, which the earlier model could not score cleanly. Usage 41,546.
All 33 claims are human-labeled pass; dataset `judge/data/realworld-v08` with the v0.8 snapshot
(`d900dda…`).

Judge ×3, prompt `6a369dd2`: **1.00 / 1.00 / 0.97**, majority **1.00 [0.90, 1.00]**, one 1/3 flip on
`FR-RW-07`. This is the first RealWorld set with no majority false alarm, and the first built for the
new judge, so it is not comparable with the 0.93 of v0.6.

2026-11-18, the probe under the new judge. `realworld-probe` (20 rows, 17 defects) judged three times
with prompt `6a369dd2`: **`fail_recall` 0.88 [0.66, 0.97]** (15 of 17), **`pass_specificity` 1.00**
(3 of 3). Per run 0.88 / 0.88 / 1.00; majority 0.88.

The two misses are the same two ambiguous mutations as under the prompt-only version: `P08`
("immediately, without a reload" on a comment step) and `P18` (a follow case that also asserts the
followed author's article appears in Your Feed). Both are readable as ordinary consequences of the
step. No clear defect is missed, and no accepted mutation is false-alarmed.
