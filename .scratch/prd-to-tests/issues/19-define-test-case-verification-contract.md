# 19: Define the test-case verification contract

**What to build:** The decided v1 contract for independently verifying a Test Case before the Gate.
This ticket is the reference for 21, 23, and 24a/24b; it does not add code itself.

## Claim

- A verdict says every in-scope case and step is **grounded** in the PRD, and each step is
  **reachable** from the state its preconditions and earlier steps provide (**continuity**).
- It does **not** claim the case is automatable, that its future locators are correct, that it
  matches the live app, that the PRD is complete, or that it deduplicates/coverages every
  requirement.
- The end-to-end proof of executability belongs to Automate, after the Gate.

## Issuer

- v1 uses Jev only. Model is pinned (`jev-1.13.0`); the question set and bands are versioned.
- Every blocking question is phrased positively so `p` is the probability the case is grounded,
  reachable, or observable.
- Jev is a different producer from the designer. The question set is still owned by this repo, and
  the required check supplies the authority.

## Verdict bands

| Verdict | Condition | Merge |
|---|---|---|
| `PASS` | `p >= 0.8` | allowed |
| `NEEDS_REVIEW` | `0.5 <= p < 0.8` | blocked until human adjudication |
| `FAIL` | `p < 0.5` | blocked; fix the case or the question set |
| `BLOCKED` | no answer, error, timeout, parse failure, or stale | blocked; retry or adjudicate |

`PASS+NOTES` is not used.

## Units and aggregation

- Step: the worst of `reasonable`, `continuity`, and `observable`.
- Case: the worst of AC alignment and all its steps.
- File: the worst of all cases.
- Precedence: `FAIL` > `BLOCKED` > `NEEDS_REVIEW` > `PASS`.
- A missing answer is `BLOCKED`; it is never treated as a pass.

## Authority

- The verdict is a **required GitHub check** on the Test Case PR head.
- `PASS` reports success. `NEEDS_REVIEW` reports `action_required`. `FAIL` and `BLOCKED` report
  failure. Every non-`PASS` state blocks merge.
- Human adjudication is an **approving PR review with a reason on the current head**. It is honored
  only for `NEEDS_REVIEW` and `BLOCKED`: the review triggers a re-run that reports success and
  records the original verdict plus the reason. A new head voids the override.
- `FAIL` has no routine override; the case or question set must change. Admin break-glass is the
  only escape hatch and is not part of normal operation.
- HTTP failures are retried by the SDK's `RetryPolicy` (2 retries with backoff by default); an
  empty answer is `BLOCKED` and is not retried. A deterministic block publishes immediately.

## Binding and invalidation

A verdict is bound to the head SHA, the artifact digest, the PRD digest, the model, the question
set, and the bands. A change to any of them makes the old verdict stale and renders it `BLOCKED`
until re-run. Advancing the base branch without changing the PRD or the artifact does not
invalidate it.

## Non-goals

- Structural validity, coverage, deduplication, priorities, and front-matter rules are ticket 22 and
  are deferred.
- Automatability, runtime behaviour, locators, and visual parity are out of scope.
- Screenshots, live-app checks, a separate verifier agent, and multi-model panels are out of scope.

## Rollout

1. Run the check in shadow mode (visible, not required) for about 10 Test Case PRs.
2. Use ticket 20 to record the `NEEDS_REVIEW` rate, false flags, and override rate.
3. Only then make the check required. Decide the admin/break-glass policy at that point.

**Blocked by:** None (can start immediately).

**Status:** ready-for-human (done; decided)

- [x] Claim and non-claims are stated
- [x] Verdict bands and thresholds are stated
- [x] Step, case, and file aggregation with precedence is stated
- [x] Required-check authority and human adjudication are stated
- [x] Binding and invalidation rules are stated
- [x] Deferred and out-of-scope work is named
- [x] Shadow-to-required rollout is stated

## Comments

**2026-10-21 — step `complete` replaced by `continuity`.** The step check now asks whether the
action is reachable from the state left by the case preconditions and earlier steps; values the
action itself enters do not need to pre-exist. The subject and parser carry `preconditions`.
Calibration evidence is in ticket 26.

**2026-10-21 — AC alignment widened.** A step or expected result is permitted when it exercises a
control the PRD describes without contradicting an AC. Only contradictions, or behaviour the PRD
does not describe at all, fail AC alignment. This lets a happy-path case operate PRD-described
optional controls (e.g. marketing checkboxes) without being flagged as invented.

**2026-10-23 — tracker cleanup.** All acceptance items are checked; status moved to `ready-for-human`.

**2026-10-24 — bookkeeping: done.**

The v1 contract is recorded in this ticket and reflected in `web_test/planning/review/verification.py`. Status → `ready-for-human (done; decided)`.
