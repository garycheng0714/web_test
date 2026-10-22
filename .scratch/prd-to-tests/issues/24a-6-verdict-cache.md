# 24a-6: Cache verdicts by digest and configuration

**What to build:** Cache the published payload in `actions/cache`, keyed by the 24a-3 cache key
(`test_case_digest + prd_digest + question_set_version + model + bands`). A cache hit publishes the
cached payload without calling Jev. `BLOCKED` is not cached.

**Blocked by:** 24a-5.

**Status:** ready-for-agent

- [ ] The workflow restores the cache with `verify-<key>` before `run`
- [ ] A cache hit skips Jev (a test uses a `SystemOne` that would fail if called)
- [ ] A miss saves the payload only for non-`BLOCKED` verdicts
- [ ] `actions/cache/save` is conditional on the `saved` output
- [ ] A different test case, PRD, or question set misses the cache
- [ ] `BLOCKED` is never written
- [ ] Tests cover hit, miss, and blocked
- [ ] `actionlint` passes

## Decisions / assumptions

- Actions cache is branch-scoped; no TTL.
- The cache key is the same value used as `external_id`.
