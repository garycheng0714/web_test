# 24: RealWorld PRD v0.7 — promise the publish redirect, and narrow the two permission requirements

**What to build:** Three edits to `.scratch/realworld/prd.md`, then the usual loop: freeze, one
designer run, human labels, a judge dataset, and three judge runs. The edit removes the last two
majority false alarms on the v0.6 set.

**Blocked by:** Nothing. Ticket 11 froze v0.6; the judge prompt is settled at `cbbb6990` (PR #53).

**Status:** ready-for-agent

**Shape:**
- Types: none. `Case`, `DesignOutput` and `LabeledClaim` keep their shape.
- Boundary: `.scratch/realworld/prd.md` (v0.7), `evals/designer/runs/<run-id>/`, and a new
  `evals/designer/judge/data/realworld-v07/`.
- Invariants: requirement count stays 28; no id is renumbered; every requirement still cites a pinned
  file or a dated observation in §9; the v0.6 dataset and the probe stay frozen and comparable.

## Why

The v0.6 set scores `pass_specificity` 0.93 with two majority failures. Neither is a judge defect;
each has its own cause.

```text
FR-RW-09   case asserts "leaves the editor"
           §9 says "來源沒有明寫發佈後導向哪裡"
           -> the judge follows §9 and fails it

FR-RW-14   requirement states two results: non-author cannot see Delete,
           and the author can
           -> one case has one identity; it asserts the first and the judge
              calls the second missing
```

`FR-RW-21` (the comment delete icon) has the same shape as `FR-RW-14`; it happened to pass in two of
three v3 runs, which is variance, not a different rule.

## Decisions this ticket encodes

- **FR-RW-09 gets the redirect as a promise.** The live demo goes to `/article/<slug>`
  (`navigate(['/article/', article.slug])`), so it becomes an observation like the post-auth
  redirect, and §9's "unspecified" note is replaced by that row. The note cannot stay: the judge reads
  the whole PRD, so "來源沒寫" is an instruction to fail.
- **FR-RW-14 and FR-RW-21 lose their second direction.** The author-side result is exercised by the
  delete journeys, `FR-RW-13` and `FR-RW-20`, whose cases click the control. Removing it leaves each
  requirement with one result that one case can assert.
- **No new requirement.** The count stays 28; this is subtraction plus one clause.

## Tasks

- [ ] `FR-RW-09`: add "導向 `/article/<slug>`" to the result, and replace its §9 inference note with a
      dated observation row.
- [ ] `FR-RW-14`: keep only "以非作者身分開啟一篇文章 → 看不到 `Delete Article`", with a note that the
      author direction is exercised by `FR-RW-13`.
- [ ] `FR-RW-21`: same shape, pointing at `FR-RW-20`.
- [ ] Header: version v0.7, "六項觀察", one v0.7 adjustment line.
- [ ] Re-freeze, record `sha256` and line count in a dated comment.
- [ ] Run the designer once (paid) with an explicit `--run-id`.
- [ ] Gate: 28 requirements, one case per requirement (an extra boundary case allowed), no duplicate,
      no invented id, no multi-requirement case.
- [ ] Label every claim in Phoenix; build `judge/data/realworld-v07/` with the v0.7 snapshot.
- [ ] Judge ×3 (paid) and compare with v0.6's 0.93 under the same prompt hash.

## Out of scope

- The probe. `realworld-probe-1` stays as it is; its mutations answer v0.6 and its rates are reported
  apart.
- Splitting other two-result requirements (`FR-RW-16` two inputs, `FR-RW-27` two pages). They pass
  under the lenient prompt; only the actor-bound one failed.
- Separating traceability notes from the text the judge reads. That is a judge-input decision, not a
  PRD edit; this ticket only stops writing "unspecified" into a requirement the judge must accept.

## Paid actions

- One designer call.
- Number of claims × 3 judge runs.

## Risks

- Removing the author direction could look like lost coverage. It is not: the delete case clicks the
  control, so a hidden button fails that case.
- The redirect is one implementation's choice. It joins the five existing implementation-level
  promises, and the header says so.
- The new set is not comparable with v0.6's 0.93 by construction; that is the point of a new version.
  Report it beside the prompt hash.
- If `pass_specificity` reaches 1.00, the set becomes pass-only again and `fail_recall` is still only
  available from the probe.

## Flow

```text
v0.6 frozen ──► three edits ──► v0.7 frozen (sha256)
                                     │
                                     ▼
                            designer x1 (paid)
                                     │
                                     ▼
                       label N claims ──► dataset
                                     │
                                     ▼
                            judge x3 (paid)
                                     │
                                     ▼
                    pass_specificity vs 0.93, same prompt
```

## Comments

Opened 2026-11-16 from the session that measured v0.6 at 0.93 and traced both remaining failures.
The FR-RW-09 failure is a PRD-meta problem, not a judge one: §9's "source does not say" note is read
as specification because the judge receives the whole PRD. The FR-RW-14 failure is a requirement-shape
problem: two results that need two identities cannot both be asserted by one case, and the judge
cannot see the sibling case that covers the other half.
