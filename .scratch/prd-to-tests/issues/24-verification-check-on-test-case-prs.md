# 24: Verify Test Case PRs at the current head

**What to build:** A required GitHub check that runs the v1 Jev verification against the current
Test Case PR head and reports `PASS`, `NEEDS_REVIEW`, `FAIL`, or `BLOCKED` bound to that head SHA.
A new head invalidates the old verdict and triggers a fresh run. `NEEDS_REVIEW` and `BLOCKED` block
until an approving PR review with a reason adjudicates them; `FAIL` has no routine override. The
check runs in shadow mode first, then becomes required.

**Blocked by:** 19 (authority and invalidation), 23 (re-reading an existing file).

**Status:** needs-triage

- [ ] The check runs on every PR; a non-Test-Case PR reports success explicitly, not `skipped` or
      pending
- [ ] `PASS` reports success, `NEEDS_REVIEW` reports `action_required`, and `FAIL`/`BLOCKED` report
      failure
- [ ] Pushing a new commit invalidates the old result and runs again
- [ ] A repeated run on the same digest reuses the cached verdict
- [ ] The check summary lists step, case, and file findings with probabilities and digests
- [ ] An approving review with a reason re-runs `NEEDS_REVIEW`/`BLOCKED` as success, records the
      original verdict and reason, and is void on a new head
- [ ] `FAIL` ignores approvals; only admin break-glass can bypass it
- [ ] `BLOCKED` retries once automatically before adjudication
- [ ] The result is idempotent: repeated runs update one check and do not add duplicate comments
- [ ] The workflow has `checks: write`; branch protection requires the check; shadow-to-required and
      the break-glass policy are documented
- [ ] Verified live on a Test Case PR, not only in tests
