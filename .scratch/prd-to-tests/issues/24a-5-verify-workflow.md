# 24a-5: Wire the shadow verification workflow

**What to build:** Add `.github/workflows/verify.yml` that runs on `pull_request`
(opened/synchronize/reopened) with no path filter, checks out the PR head SHA, runs `prepare` and
`run`, and publishes the check through the app token. The job stays green for any verdict; only
publishing or infrastructure failures turn it red.

**Blocked by:** 24a-4.

**Status:** ready-for-agent

- [ ] Triggers on opened/synchronize/reopened and checks out the head SHA
- [ ] A PR with no test-case artifact publishes success explicitly
- [ ] One artifact is reviewed; multiple artifacts fail with a clear reason
- [ ] The check is named `verify-test-case`; conclusions follow the mapping
- [ ] The summary lists findings, counts, and binding digests
- [ ] A rerun updates the same check for the head SHA
- [ ] The workflow has `checks: write`; the app token has Checks permission
- [ ] `TYPESAFE_API_KEY` is available to the run
- [ ] `actionlint` passes; the job is shadow (not required)
- [ ] Verified live on a Test Case PR

## Decisions / assumptions

- Same-repo PRs only; fork PRs are out of scope for v1.
- The workflow job itself also appears as a check; `verify-test-case` is the one that carries the
  verdict.
- Cache comes in 24a-6; this ticket runs the review on every event.
