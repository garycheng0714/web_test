# 26: Calibrate the verifier's complete dimension

**What to build:** Resolve the good-case false flags the eval harness found in the `complete`
dimension, then make the v3 kill criteria pass (or record an explicit, justified exception) before
the verification check becomes required.

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

- [ ] Reproduce the live result with the ticket 20 eval command
- [ ] Classify the cause: question wording, bands, or fixture data
- [ ] Choose one fix: adjust the `complete` question, narrow when it applies, adjust the bands, or
      record a justified exception
- [ ] Re-run the v3 eval; kill criteria pass, or the exception is documented
- [ ] Confirm the other dimensions still catch their bad variants
- [ ] `uv run pytest` passes
- [ ] 24b stays unrequired until this is resolved

## Comments

Likely context, not yet proven: old v3 only added `complete` to B4, while the current question set
asks `complete` for every step. Do not weaken `complete` just to make good cases pass; re-check that
B1–B4 remain caught.

Related: ticket 20 (harness and live result), ticket 24b (required-check flip).
