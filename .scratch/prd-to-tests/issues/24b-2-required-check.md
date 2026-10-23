# 24b-2: Require the verification check

**What to build:** Turn the shadow `verify-test-case` check into a required check on `main`, document
the shadow-to-required rollout and the admin break-glass policy, and verify it live on a Test Case
PR. This needs repository admin; it is not an agent-only change.

**Blocked by:** 24b-1 (adjudication); ticket 26's calibration is already satisfied.

**Status:** ready-for-human

- [ ] Branch protection on `main` requires the `verify-test-case` check
- [ ] The shadow-to-required rollout is documented: the evidence used, the observation period, and
      the decision point
- [ ] The break-glass policy is documented: only a repository admin bypasses the check, the reason is
      recorded, and the bypass is followed by a re-run after the fix
- [ ] The README stops describing `verify-test-case` as a shadow check and states that it is required
- [ ] A live Test Case PR verifies the required check and the adjudication path
- [ ] The live PR confirms that a new head voids the previous approval
- [ ] `FAIL` remains unmergeable without an admin bypass
- [ ] The live result is recorded in this ticket

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
