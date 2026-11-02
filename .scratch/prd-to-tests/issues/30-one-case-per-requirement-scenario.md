# 30: One case per requirement scenario

**What to build:** Stop merging two requirements into one case when the second requirement has no
distinct scenario. The designer should emit one case per FR scenario, so each automated test
isolates one requirement and does not repeat another requirement's steps.

**Blocked by:** None.

**Status:** ready-for-agent

**No boundary change.** This is a skill/policy change plus an eval signal; `Case` and
`DesignOutput` keep their shape.

## Evidence

From the house-skill run `house-automationexercise-20261029` on
`.scratch/automationexercise/prd.md` (31 claims, 6 multi-FR cases), three claims were labeled
`duplicated` because the FR had no scenario of its own:

- `case-12-functional` claims `FR-PRD-07` and `FR-CART-01`, but both are verified by the same
  Home-page recommended-items flow. `FR-CART-01` (cart rows show price/quantity/total) should be
  exercised from a different add-to-cart entry point.
- `case-18-functional` claims `FR-ENG-02` and `FR-CART-05` with one subscription flow. The PRD says
  the Cart placement behaves the same as Home, but automation still needs two tests: one per
  placement, so a failure names the broken placement.
- `case-22-functional` claims `FR-ORD-01` and `FR-ORD-02`. Reaching checkout (ORD-01) and verifying
  Delivery/Billing addresses (ORD-02) are separate scenarios; ORD-01 should not assert the address
  block at all.

## Tasks

- [x] House skill (`.agents/libraries/test_case_designer/qa-test-case-generation/SKILL.md`): one
      FR per case, exactly one `requirement_ids` entry; specific FR over a general one; no
      precondition FRs; sequential FRs split with `preconditions`.
- [x] Resolve the boundary with ticket 16: deduplicate identical cases, not distinct FR scenarios.
      Two placements of the same behaviour are two scenarios.
- [x] When a multi-FR case remains, every claim must point at a step that verifies that FR; a claim
      that only rides on another FR's steps is not allowed.
- [x] Re-run the designer on `.scratch/automationexercise/prd.md`; the case count rises only where
      a scenario is genuinely new, and no exact duplicate cases appear.
- [x] Confirm `duplicated` has no candidates after the PRD normalization: the final run has 0
      multi-FR cases, so no claim can be `duplicated` by construction.
- [x] Run `uv run pytest`, `basedpyright`, `lint-imports`, `ruff check`, `ruff format --check`.

## Out of scope

- PRDs other than `prd/register-login.md`, `prd/live-evidence.md`, and
  `.scratch/automationexercise/prd.md`.
- The evaluator's label definitions (`duplicated` already exists).
- Re-running the old vendored skill.

## Risks

- Splitting cases increases the case count and repeats steps by design. That is the trade the ticket
  makes: per-FR isolation beats a smaller suite when the output is automation.
- Ticket 16 asked for a dense suite. The rule here narrows it: dense means no duplicate cases, not
  one case per behaviour cluster.
- The designer may split too aggressively (one case per step). The acceptance check is that each
  split case has its own scenario and acceptance criteria, not one scenario per assertion.

## PRD normalization (2026-10-30)

The split run still produced three multi-FR cases because the PRDs described one user flow at step
granularity. With approval, the PRDs were normalized:

- `FR-ACC-01` + `FR-ACC-02` merged into one registration FR (both PRDs).
- `FR-UI-02` removed: "every source TC starts at the home page" is a property of the reference test
  suite, not a product requirement.
- `FR-ENG-02` narrowed to the Home placement; `FR-CART-05` owns the Cart placement.
- Traceability matrices updated; `prd/live-evidence.md` now says it covers only the first AC.
- Requirements: 27 -> 25.

## Result (2026-10-30)

Run `house-split-automationexercise-20261030`, trace `df032703e237eadf74b8e8b6bc0326d1`, on the
same PRD:

| | before | after |
| --- | --- | --- |
| cases | 23 | 26 |
| claims | 31 | 29 |
| multi-FR cases | 6 | 3 |
| exact duplicate cases | 0 | 0 |
| missing requirements | 1 (`FR-UI-02`) | 0 |

Targeted checks:

- `FR-PRD-07` and `FR-CART-01` are now separate cases: `case-13` (Home recommended items) and
  `case-14` (two products from the product list, rows show price/quantity/total).
- `FR-ENG-02` Home and Cart placements are separate: `case-18` (Home footer) and `case-19` (Cart
  footer).
- `FR-ORD-01` (`case-20`) no longer asserts Delivery/Billing; that is `case-21` (`FR-ORD-02`).

Remaining multi-FR cases: `case-1` (`FR-ACC-01` + `FR-ACC-02`, two-step signup with steps for
each), `case-19` (`FR-CART-05` + `FR-ENG-02`, the Cart placement), `case-26` (`FR-UI-01` +
`FR-UI-02`, the Home-load step inside the scroll case). Label these before closing the ticket.

## Comments

Opened 2026-10-29 from the designer eval on `.scratch/automationexercise/prd.md`. The `duplicated`
label was introduced during the same session; see `.scratch/designer-evals/spec.md`.

## Result after normalization (2026-10-30)

Run `house-normalized-automationexercise-20261030` on the normalized PRD:

| | split run | normalized |
| --- | --- | --- |
| cases | 26 | 27 |
| claims | 29 | 27 |
| multi-FR cases | 3 | 0 |
| missing requirements | 0 | 0 |
| exact duplicate cases | 0 | 0 |

- Every case has exactly one FR.
- `case-1` (`FR-ACC-01`) runs the whole registration flow and stops at the logged-in header.
- `case-18` (`FR-CART-05`) and `case-25` (`FR-ENG-02`) are the Cart and Home subscription cases.
- With multi-FR = 0, `duplicated` has no candidates; no further labeling is needed for this check.
