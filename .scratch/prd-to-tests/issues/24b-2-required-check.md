# 24b-2: Require the verification check

**What to build:** Turn the shadow `verify-test-case` check into a required check on `main`, document
the shadow-to-required rollout and the admin break-glass policy, and verify it live on a Test Case
PR. This needs repository admin; it is not an agent-only change.

**Blocked by:** 24b-1 (adjudication); ticket 26's calibration is already satisfied.

**Status:** ready-for-human

- [x] Branch protection on `main` requires the `verify-test-case` check
- [x] The shadow-to-required rollout is documented: the evidence used, the observation period, and
      the decision point
- [x] The break-glass policy is documented: only a repository admin bypasses the check, the reason is
      recorded, and the bypass is followed by a re-run after the fix
- [x] The README stops describing `verify-test-case` as a shadow check and states that it is required
- [x] A live Test Case PR verifies the required check and the adjudication path
- [x] The live PR confirms that a new head voids the previous approval
- [x] `FAIL` remains unmergeable without an admin bypass
- [x] The live result is recorded in this ticket

## Decisions / assumptions

- Use the kept `test-case/test-case-register-login.md` as the live Test Case artifact. It stays
  untracked on `main` and is added on the live PR branch.
- The repository admin owns the branch-protection change and the break-glass action. The agent can
  prepare the ticket and the live PR, but cannot promise the protection setting.
- Enabling "dismiss stale approvals on new commits" is recommended as defense-in-depth, but the
  workflow's `review.commit_id == head SHA` check is the actual guard.
- A bypass is not a routine override: `FAIL` still requires a fix to the Test Case or question set.

## Out of scope

- The adjudication implementation and workflow trigger are 24b-1.
- New verification dimensions and deterministic checks.

## Comments

**2026-10-23 — branch protection confirmed.** `main` uses classic branch protection, not rulesets.
Required checks are `test` (GitHub Actions, app id `15368`) and `verify-test-case` (app id `5369660`,
`web-test-qa-flow`, the same app as PR #11). `enforce_admins` is `false`, so the admin bypass exists;
`required_pull_request_reviews` is `null`. README now says `verify-test-case` is required and records
the break-glass rule.

**2026-10-23 — live-test blockers.** The kept artifact returns `PASS` in a local Jev run
(`ac_2` p=0.82), so approving it would not exercise the override. Use a `NEEDS_REVIEW` variant, or
force `BLOCKED` by temporarily removing `TYPESAFE_API_KEY`. Separately, GitHub rejects a reviewer
approving their own pull request, so the live PR needs a second reviewer identity: either a second
account/colleague, or an app-authored PR opened with the `web-test-qa-flow` token so the repository
owner can approve it.

**2026-10-23 — live NEEDS_REVIEW variant prepared.** Branch `verify/live-adjudication` (commit
`8932447`) adds `test-case/test-case-live-adjudication.md`, a copy of the real artifact with Case 2
step 3's expected result shortened to "The account is created." Three local Jev runs stayed
`NEEDS_REVIEW` (`ac_2` 0.79 / 0.79 / 0.81; `step_2_3_observable` 0.63 / 0.59 / 0.57). This gives the
live test a real non-PASS verdict without touching `TYPESAFE_API_KEY`.

## Rollout

- Evidence: ticket 26's calibration passed (caught 4/4, hard_fail 4/4, B4 continuity p=0.13, G1/G2
  zero false flags); 24a-5 was verified live on PR #11; 24b-1 has unit coverage for the override,
  cache, and FAIL guard; 24b-2's live PR #12 confirms the real GitHub path.
- Observation period: 2026-10-21 to 2026-10-23. One live shadow Test Case PR (#11), fewer than the
  ~10 suggested by ticket 19. The repository admin accepted the accelerated rollout and set the
  required check on 2026-10-23.
- Decision point: after 24b-1 landed and PR #12 confirmed the override and new-head invalidation.
- Break-glass: repository admins only; record the reason, re-run after the fix, and never treat a
  bypass as routine. `FAIL` still requires a Test Case or question-set change.

**2026-10-23 — live PR #12.** The PR was opened by `web-test-qa-flow[bot]` from
`verify/live-adjudication` so the repository owner could approve it without self-approval.

- **H1 `8932447`** (NEEDS_REVIEW variant): `verify-test-case` was `NEEDS_REVIEW` /
  `action_required`; `test`, `typecheck`, `contracts`, `workflows`, and `verify` were green; merge
  was `BLOCKED`. An approving review with a reason triggered `adjudicate` (run `39951857317`,
  success). The check became `success`, the summary recorded `NEEDS_REVIEW`, the reason, and `H1`,
  and merge became `CLEAN`.
- **H2 `7dd10da`** (empty commit): `verify-test-case` was `NEEDS_REVIEW` / `action_required` with no
  override summary, even though the review remained `APPROVED`; merge was `BLOCKED`. This confirms a
  new head voids the previous approval.
- **H3 `75749bc`** (deliberate FAIL variant): `verify-test-case` was `FAIL` / `failure`; merge was
  `BLOCKED`; the other required checks were green. This confirms `FAIL` is unmergeable without an
  admin bypass.
- Break-glass: direct pushes `2ce5649` and `1292f75`/`9ba6a3c` to `main` bypassed the required
  checks to add the docs and the temporary live-PR workflow. The reason is recorded here; the
  temporary workflow was removed after the live test. A cleanup push for this ticket and the
  workflow removal is the same break-glass path.
