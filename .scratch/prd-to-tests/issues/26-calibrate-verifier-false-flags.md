# 26: Calibrate the verifier's continuity dimension

**What to build:** Resolve the good-case false flags the eval harness found in the step completeness
/ continuity dimension, then make the kill criteria pass (or record an explicit, justified exception)
before the verification check becomes required.

Live v3 result from ticket 20:

- caught 4/4
- hard_fail 4/4
- bad blocked 0
- good false flags **4**, all on `complete`
  - G1 step 3 p=0.51
  - G2 step 1 p=0.54
  - G2 step 2 p=0.68
  - G2 step 3 p=0.71
- needs-review rate 2/6 cases
- kill criteria **FAIL**

**Blocked by:** 20 (eval harness).

**Status:** needs-triage

- [x] Reproduce the live result with the ticket 20 eval command
- [x] Classify the cause: question wording, bands, or fixture data
- [x] Choose one fix: adjust the `complete` question, narrow when it applies, adjust the bands, or
      record a justified exception
- [x] Re-run the v3 eval; kill criteria pass, or the exception is documented
- [x] Confirm the other dimensions still catch their bad variants
- [x] `uv run pytest` passes
- [x] 24b stays unrequired until this is resolved

## Comments

Likely context, not yet proven: old v3 only added `complete` to B4, while the current question set
asks `complete` for every step. Do not weaken `complete` just to make good cases pass; re-check that
B1–B4 remain caught.

Related: ticket 20 (harness and live result), ticket 24b (required-check flip).

**2026-10-21 — `complete` replaced by `behavior`.**

Experiments on `complete` (per-step and case-level) were unstable on normal sequential workflows:

- Per-step `complete` on the real artifact: 5/16 steps complete; Case 1 step 3 p=0.39.
- Case-level `complete`: G2 p=0.48 (false flag), real artifact 1/7 cases complete.
- Sequence-aware prompts and preconditions alone did not fix it.

Decision: replace `complete` with `behavior` — does the action in a step produce its expected
result, given the case preconditions and earlier steps? `ReviewCase`, the parser, the design
adapter, and the eval fixture now carry `preconditions`; B4's expected dimension is `behavior`.

Results after the swap:

- Real artifact: 16/16 behavior, 16/16 reasonable, 16/16 observable; AC alignment 6/7 (Case 2
  p=0.74 → `NEEDS_REVIEW`).
- Eval, 3 runs, same verdicts: caught 4/4, hard_fail 4/4, B4 `behavior` p=0.05.
- G1 clean. G2 still has 4 false flags: AC alignment p=0.78–0.79, behavior steps 1–3 p=0.75–0.77.
- Kill criteria still **FAIL** on `good_false_flags`; `24b` stays unrequired.

Preconditions × wording comparison (eval 3 runs each; real artifact 16 steps):

| preconditions in subject | question mentions them | G2 behavior p | real artifact behavior |
|---|---|---|---|
| yes | yes (current) | 0.75–0.77 | 16/16 |
| yes | no | 0.68–0.74 | 15/16 (step 1 p=0.77) |
| no | no | 0.33–0.74 | 4/16 |
| no | yes (confounded) | 0.38–0.74 | 5/16 |

The preconditions data drives the check; the wording mention only helps marginally. Asking about
preconditions that are absent adds noise, so the current wording is kept.

**2026-10-21 — `behavior` refined into `continuity` (final).**

`behavior` still left 3 G2 false flags (0.73–0.77) because "produce its expected result" mixed two
claims: continuity (can the step run from the current state?) and sufficiency (does it reach the
expected result?). The fill-a-form steps are continuous but do not literally produce the whole form
state, so they scored just under the band.

`continuity` asks only whether every input and condition the action needs already exists from the
preconditions or earlier steps, and states that values the action itself enters or selects do not
need to pre-exist.

Results (3 runs, reproduced):

- Eval: caught 4/4, hard_fail 4/4, B4 `continuity` p=0.13, G1/G2 zero false flags,
  kill criteria **PASS**.
- Real artifact: 16/16 continuity; `NEEDS_REVIEW` only from AC alignment (Case 2 p=0.75).
- Control without preconditions: real artifact 5/16, G2 3–4 false flags; continuity still depends on
  the preconditions data.

Adopted: `CheckDimension.STEP_CONTINUITY`, question ids `_continuity`, fixture B4 expected dimension
`continuity`. Ticket 19's contract wording and ticket 20's comments were updated.
