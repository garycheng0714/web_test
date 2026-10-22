# 24a-5: Wire the shadow verification workflow

**What to build:** Add `.github/workflows/verify.yml` that runs on `pull_request`
(opened/synchronize/reopened) with no path filter, checks out the PR head SHA, runs `prepare` and
`run`, and publishes the check through the app token. The job stays green for any verdict; only
publishing or infrastructure failures turn it red.

**Blocked by:** 24a-4.

**Status:** ready-for-human

- [x] Triggers on opened/synchronize/reopened and checks out the head SHA
- [x] A PR with no test-case artifact publishes success explicitly
- [x] One artifact is reviewed; multiple artifacts fail with a clear reason
- [x] The check is named `verify-test-case`; conclusions follow the mapping
- [x] The summary lists findings, counts, and binding digests
- [x] A rerun updates the same check for the head SHA
- [x] The workflow has `checks: write`; the app token has Checks permission
- [x] `TYPESAFE_API_KEY` is available to the run
- [x] `actionlint` passes; the job is shadow (not required)
- [ ] Verified live on a Test Case PR

## Decisions / assumptions

- Same-repo PRs only; fork PRs are out of scope for v1.
- The workflow job itself also appears as a check; `verify-test-case` is the one that carries the
  verdict.
- Cache comes in 24a-6; this ticket runs the review on every event.

## Comments

**2026-10-23 — implemented.** `.github/workflows/verify.yml` runs on opened/synchronize/reopened
with no path filter, skips fork PRs, mints an app token with `permission-checks: write`, checks out
the PR head SHA with full history, and runs `prepare` then `run`. Changed paths come from
`git diff --name-only --diff-filter=ACMR base...head`, so deleted files are ignored. The verification
input goes to `.verify/` (gitignored); `prepare` keeps its `key=` output for 24a-6. The job times out
after 15 minutes and stays green for verdicts; publish or infrastructure failures exit non-zero.
`actionlint` passes for all workflows. `Checks: write` was granted to `web-test-qa-flow`, the three
secrets are present, and the first run on the workflow PR will confirm the token. Live verification
on a Test Case PR is still pending.
