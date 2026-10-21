# 24a: Verify Test Case PRs in shadow mode

**What to build:** An always-run GitHub check that runs the v1 Jev review against the current Test
Case PR head and publishes `PASS`, `NEEDS_REVIEW`, `FAIL`, or `BLOCKED` bound to that head SHA.
The check is visible but not required yet; it gathers data before 24b.

**Blocked by:** 19 (authority and invalidation), 23 (parser and local review).

**Status:** ready-for-agent

- [ ] The workflow triggers on `pull_request` opened/synchronize/reopened and checks out the PR head
      SHA
- [ ] A non-Test-Case PR reports success explicitly; it must not be `skipped` or pending
- [ ] Exactly one changed `test-case/*.md` file is reviewed; zero or multiple files fail with a clear
      reason
- [ ] The PRD is resolved as `prd/<front-matter id>.md`
- [ ] The check is named `verify-test-case`; `PASS` reports success, `NEEDS_REVIEW` reports
      `action_required`, and `FAIL`/`BLOCKED` report failure
- [ ] The check summary lists per-check findings, counts, and binding digests
- [ ] The same digest and configuration reuse a cached verdict
- [ ] `BLOCKED` retries once before publishing
- [ ] Check creation/update is idempotent for a head SHA
- [ ] The workflow has `checks: write`, and the GitHub App has Checks permission
- [ ] Verified live on a Test Case PR; the check is not required yet

## Decisions / assumptions

- One Test Case file per PR, matching `automate.yml`; multiple files fail for v1.
- PRD path comes from the Test Case front-matter `id`.
- Cache key: `test_case_digest + question_set_version + model + bands`.
- Check name: `verify-test-case`.
- Shadow only; branch protection, adjudication, and the required check are 24b.
