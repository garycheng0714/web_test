# 09: Add a held-out second PRD (TodoMVC)

**What to build:** A second PRD, extracted from a public specification rather than reverse-engineered,
so the judge's criteria and the designer's output can be checked on a different document. Then run
the designer, label the claims, and run the judge three times. The numbers are reported separately
from `automationexercise`; this PRD never enters the production pipeline.

**Blocked by:** Nothing. Ticket 07 finished the unit and the fixture; this is what that ticket said a
second PRD is for.

**Status:** ready-for-agent

**Shape:**
- Types: none. `DesignOutput`, `Case`, `AcceptanceCriterion` and `LabeledClaim` keep their shape.
- Boundary: `.scratch/todomvc/prd.md` (not `prd/`, which would trigger `plan.yml`), the run under
  `evals/designer/runs/`, and a separate judge dataset under `judge/data/`.
- Invariants: the spec is pinned by commit (`d040877f`); every requirement cites a spec section and
  adds no behaviour the spec does not state; the PRD is frozen once the first judge run starts; the
  dataset never mixes rows from the two PRDs.

## Why TodoMVC

`tastejs/todomvc`'s `app-spec.md` is a public behavioural specification and
`https://demo.playwright.dev/todomvc/` is live (200). The alternatives failed on the "public spec"
requirement: RealWorld's demo is gone (404) and only the API spec remains; Sauce Demo, the-internet
and demoblaze publish no spec; `automationexercise` is already the dev PRD.

## How the PRD was built

The extraction rules are in the PRD header and were written before the PRD: only user-visible
outcomes, one requirement per action sequence, the spec's own sentences where possible, gaps in
§11 rather than invented, and everything dropped listed in §10. `app-spec.md` is implementation-first
(directory structure, npm, CSS classes), so the lossy part is deliberate and reviewable.

This is **not** a neutral document: the specification is not ours, but the cut is. It can test
whether the judge's scope rule works on another granularity; it cannot claim to be free of our
judgement. That sentence belongs in any report built on it.

## Tasks

- [x] Write `.scratch/todomvc/prd.md` from `app-spec.md` @ `d040877f`, with the extraction rules,
      the traceability table, the dropped list, and §11 gaps (v0.1).
- [x] Re-cut to v0.2 by the branch rule: 10 -> 21 requirements, ids out of the requirement text,
      the corrected cut recorded in §10.1, §9 re-synced.
- [x] v0.3 after review: 22 requirements, Enter and blur split, routes described by the footer
      links, §10.2 records the four corrections.
- [x] v0.5: the determinable §11 items written into requirements from the reference
      implementation, three requirements added, §11 becomes non-goals. 25 requirements.
- [x] Confirm v0.1 parsed as 10, v0.2 as 21, v0.3 as 22, all with no acceptance criteria.
- [x] Freeze the PRD at v0.5: `sha256` `7bbd16ef…`, recorded in the comment below.
- [x] Run the designer once on v0.3 (paid): 22 cases, one requirement each.
- [ ] Run the designer once on v0.5 (paid) and check the gate: about 25 cases, one requirement each,
      no invented requirement ids (run `todomvc-v03-20261106`).
- [ ] Label the claims in Phoenix, using the v0.8 modes.
- [ ] Build the dataset with `build_claims.py`, under a name that reads the TodoMVC PRD.
- [ ] Run the judge three times (paid) and report `pass_specificity`, `fail_recall`, the confusion
      counts, and the three-run agreement, separately from the `automationexercise` baseline.

## Out of scope

- `prd/todomvc.md` and the production pipeline. A new file under `prd/` triggers `plan.yml` and a
  paid designer run with a Gate PR.
- Automating TodoMVC with Playwright.
- Changing the judge prompt before the first run on this PRD. After that, a prompt change would be a
  new version, not a fix.
- Merging this dataset's rows into `automationexercise`.

## Risks

- The cut is ours: requirement granularity and wording shape what the judge sees.
- The spec is thin in nine places (§11). A designer that fills those gaps is showing a real defect,
  but a labeler may read the gaps as reasonable.
- 10 claims means wide Wilson intervals; this PRD adds a second domain, not statistical power.
- The live demo can drift from the spec. Grounding is not part of this ticket.

## Comments

Opened 2026-11-05. Ticket 07's baseline is pass-only, so `fail_recall` is `n/a`; the judge's scope
rule was written after reading the `automationexercise` disagreements. This PRD is the first
document the judge and the rule have not seen.

2026-11-05: the PRD is written and frozen. `sha256` of `.scratch/todomvc/prd.md` at freeze time is
`8444fb2adf98ce33562d9ff9701ed6683a6043bd3a7088fe3838b965bd6e97e2` (184 lines, 10 requirements, no
acceptance criteria). Any later edit invalidates the comparison and belongs in a new version.

2026-11-06: v0.1 ran as `todomvc-20261105` and produced 22 cases for 10 requirements. The designer
split what the PRD had merged: editing became four cases (enter / commit / clear-to-delete / escape),
routing four, the new-todo input three, the counter three. The branch rule says those are separate
journeys — a branch from a shared state gets its own requirement, the same way `FR-ACC-04` was split
— so the PRD was too coarse, not the designer.

v0.2 re-cuts it to 21 requirements, removes the HTML ids from the requirement text (`FR-TODO-01`
had used `#main`/`#footer` as its subject and "承載" as its verb), and records the corrected cut in
§10.1 so the change is reviewable. Two v0.1 merges survived the re-cut because they are one action
with two results: the counter display, and the reload (content + no item left in edit mode).

The v0.2 `sha256` is `3c949b11544bafcd761632cd1cd3f62c8b919c0d742af0bf01c4c3c3bc58266f`. The v0.1
run must not be labeled or compared; its 22 cases answer a PRD that no longer exists. The next
designer run on v0.2 is a paid call.

2026-11-06, v0.3: four review corrections before any run.

- Mark-all now states both directions; the spec says the checkbox *toggles* all todos.
- `FR-TODO-09` names what hides: the checkbox and the remove button. The spec says "the other
  controls"; the concrete pair comes from the template, and §9 says so.
- Saving split by trigger: `FR-TODO-10` is Enter, `FR-TODO-11` is blur. Deleting an empty title
  keeps both triggers, because the spec describes the outcome, not the trigger.
- Routing is described by the footer links the user clicks; the hash stays as background. The
  default filter is now its own requirement.

22 requirements. `sha256` `2cf895ee9c924eb8c81a4f359a78d15659a234ed5095a4c6bb54c872bec3255a`. The
v0.1 and v0.2 files are superseded and no run on either may be labeled or compared.

2026-11-06, gate run on v0.3: `todomvc-v03-20261106`, `deepseek-v4.1-flash`.

| | result |
| --- | --- |
| requirements | 22 |
| cases | 22 |
| claims | 22 (one requirement each) |
| distinct requirements | 22 |
| requirements per case | 1 for all 22 |
| duplicate cases | 0 |
| invalid ids | 0 |
| usage | prompt 11,107 / completion 12,323 / cache read 4,480 / total 23,430 |
| open questions | 11 |

The v0.1 run answered the same PRD with 22 cases for 10 requirements; after the re-cut the designer
emits one case per requirement, so the extra cases were the design's reading of a coarse PRD, not a
taste for splitting. The v0.1 run stays unlabeled.

Next: label 22 claims in Phoenix, build the dataset, judge x3 (66 paid calls).

2026-11-06, judge baseline on the held-out PRD. Dataset `judge/data/todomvc/` (22 rows: 21 pass,
1 fail), frozen PRD v0.3, prompt `8835420e`, `kimi-k2.7-code`, three runs.

| run | fail verdicts | fail recall | pass specificity |
| --- | --- | --- | --- |
| `todomvc-baseline-run1` | 4 | 0.00 [0.00, 0.79] | 0.86 [0.65, 0.95] |
| `todomvc-baseline-run2` | 4 | 0.00 | 0.86 |
| `todomvc-baseline-run3` | 3 | 0.00 | 0.90 [0.71, 0.97] |
| majority | 3 | 0.00 [0.00, 0.79] | 0.86 [0.65, 0.95] |

19 of 22 claims had the same verdict in all three runs.

**The missed fail is not judgeable.** `case-14 -> FR-TODO-14` is labeled `prd_gap`: the PRD says
`0 items` where the app renders `0 items left`, and the case copies the PRD. The judge is given the
PRD as truth, so it passes the case every time. `claim_alignment` compares a case to its PRD; this
label compares the PRD to the app. Two different questions. Either the row should be pass with a
reason, or `prd_gap` rows are excluded from `fail_recall` — the judge cannot catch them.

**The three stable false alarms:**

- `case-16 -> FR-TODO-16` (3/3): the judge says "the button appears when a todo is completed" is not
  stated by FR-TODO-16. FR-TODO-15 states the button is used when completed items exist, and the
  case's own step produces the completed item. The judge read one requirement in isolation.
- `case-5 -> FR-TODO-05` (2/3): the judge objects to asserting the clicked checkbox is checked and
  the other todo is unchanged. The checkbox is the control the step clicked; the second clause is a
  "nothing else changed" note, which the rubric says is not an assertion.
- `case-12 -> FR-TODO-12` (2/3): mixed. The scenario title claims Enter and blur but the steps only
  do Enter (a real title/steps mismatch), and "leaves edit mode" is not stated. The second reason is
  pedantic, the first is fair.

One more, not majority: `case-17 -> FR-TODO-17` failed 1/3 for asserting list order, which the PRD's
§11 explicitly leaves undefined. That catch is correct; the human label missed it. It is also
unstable.

So the held-out PRD did its job: it shows the judge is not ready to gate. Specificity around 0.86 on
a document it has not seen, with two of three stable failures caused by reading requirements in
isolation and treating a "nothing else changed" note as an assertion. `fail_recall` stays
uninformative with one negative, and that negative is outside the judge's question.

2026-11-10, v0.5: the §11 items that the reference implementation settles are now requirements.

| source | written into |
| --- | --- |
| `todomvc-app-css` (`li:hover .destroy`, `.destroy { display:none }`) | `FR-08` also hides on hover-out; `FR-05` is a strikethrough with grey text |
| `todomvc-app-template/index.html` (`.main` hidden when empty, toggle-all inside it) | `FR-01` includes the mark-all checkbox |
| spec ("number of active todos", "filter on a model level") | `FR-14` ignores the filter; `FR-24` new item follows the filter |
| hash routing | `FR-25` back/forward changes the filter |
| editing saved only on Enter/blur + editing mode not persisted | `FR-17` drops an unsaved edit on reload |

Three new requirements: `FR-TODO-23` remove (click), `FR-TODO-24` adding under a filter,
`FR-TODO-25` back/forward. 22 -> 25. `FR-TODO-23` is the only inference: the spec never says what
the remove button does; the name and the `destroy` class carry it, and §9 says so.

§11 is now "non-goals": no cross-tab sync, no id/order rule, no title length limit, no touch
support. Those are scope decisions, not invented behaviour.

The header's nature changed from "extracted from a spec" to "spec + reference implementation". The
PRD is still not ours in content, but it is now a derivation across three artifacts.

`sha256` `7bbd16ef70c97e7ba5600581575012440091e531a84360b8c1d56d811cb33baa`. The v0.3 dataset stays
frozen; the v0.4 run (skill-state) is superseded and must not be labeled.
