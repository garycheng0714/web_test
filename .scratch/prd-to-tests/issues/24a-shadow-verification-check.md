# 24a: Verify Test Case PRs in shadow mode

**What to build:** An always-run GitHub check that runs the v1 Jev review against the current Test
Case PR head and publishes `PASS`, `NEEDS_REVIEW`, `FAIL`, or `BLOCKED` bound to that head SHA. The
check is visible but not required yet; it gathers data before 24b.

This is an umbrella ticket. The work is split into six subtickets; this ticket closes when all of
them are done and the check is verified live.

**Blocked by:** 24a-1, 24a-2, 24a-3, 24a-4, 24a-5, 24a-6.

**Status:** ready-for-agent

## Subtickets

- [ ] **24a-1** Jev retry seam (`retry_once` in `jev.py`)
- [ ] **24a-2** Check publisher (`find_check_run`, `publish_check`)
- [ ] **24a-3** Resolver and cache key (pure)
- [ ] **24a-4** Verdict CLI (`prepare` / `run`)
- [ ] **24a-5** Workflow and live shadow check
- [ ] **24a-6** Cached verdict

## Acceptance

| Requirement | Covered by |
|---|---|
| `pull_request` opened/synchronize/reopened; checkout the head SHA | 24a-5 |
| A non-Test-Case PR reports success explicitly; one artifact is reviewed; zero or more than one fails with a reason | 24a-3, 24a-4, 24a-5 |
| The PRD is resolved as `prd/<front-matter id>.md` | 24a-3, 24a-4 |
| The check is named `verify-test-case`; `PASS` → success, `NEEDS_REVIEW` → action_required, `FAIL`/`BLOCKED` → failure | 24a-2, 24a-4 |
| The summary lists per-check findings, counts, and binding digests | 24a-4 |
| The same digest and configuration reuse a cached verdict | 24a-6 |
| A failed Jev call or empty answer retries once; a deterministic block publishes immediately | 24a-1, 24a-4 |
| Creation/update is idempotent for a head SHA | 24a-2 |
| The workflow has `checks: write` and the App has Checks permission | 24a-5 |
| Verified live on a Test Case PR; still shadow | 24a-5 |

## Decisions / assumptions

- One Test Case file per PR; multiple files fail for v1.
- PRD path comes from the Test Case front-matter `id`.
- Cache key: `test_case_digest + prd_digest + question_set_version + model + bands`. The original
  decision omitted `prd_digest`; the verdict binds to it, so it is included.
- `BLOCKED` is published but not cached.
- Retry only for a Jev call exception or an empty answer, once, with no backoff.
- Zero changed artifacts means "nothing to verify" and publishes success; more than one publishes
  failure with the file list.
- Check name: `verify-test-case`.
- Publishing goes through the Python `GitHub` adapter, not shell `gh api`.
- Same-repo PRs only for v1; fork PRs are out of scope.
- Shadow only; branch protection, adjudication, and the required check are 24b.

## Comments

**2026-10-21 — split.** The original ticket mixed a transport retry, a GitHub adapter, pure
resolution, a CLI, workflow wiring, and caching. Splitting keeps each change testable on its own and
gives the workflow an end-to-end tracer at 24a-5 before the cache is added at 24a-6.

```text
24a-1 retry ──────────┐
24a-2 publisher ──────┼─> 24a-4 verdict CLI ──> 24a-5 workflow ──> 24a-6 cache
24a-3 resolver/key ───┘
```

```text
pull_request opened / synchronize / reopened
  │
  ▼
checkout PR head SHA + uv sync
  │
  ▼
changed test-case artifacts?
  ├─ 0 ──> success: no Test Case file in this PR
  ├─ >1 ─> failure: list the files
  └─ 1 ──> read front-matter id -> prd/<id>.md
             ├─ missing ──> failure: reason
             └─ found ───> cache key = digests + question-set + model + bands
                            │
                            ▼
                          cache hit?
                            ├─ yes ──> cached verdict
                            └─ no ──> run review; retry once on a failed call or empty answer
                                       save verdict unless BLOCKED
                            │
                            ▼
                          verdict -> conclusion
                          PASS=success
                          NEEDS_REVIEW=action_required
                          FAIL / BLOCKED=failure
                            │
                            ▼
                          publish verify-test-case
                          PATCH if it exists on the head SHA, else POST
```
