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
      the traceability table, the dropped list, and §11 gaps.
- [x] Confirm it parses as 10 requirements with no acceptance criteria.
- [ ] Freeze the PRD: record its sha in the run before the designer starts, and do not edit it after
      the first judge run.
- [ ] Run the designer once (paid) and check the gate: about 10 cases, one requirement each, no
      invented requirement ids.
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
