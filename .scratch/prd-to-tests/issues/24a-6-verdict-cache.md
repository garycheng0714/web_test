# 24a-6: Cache verdicts by digest and configuration

**What to build:** Cache the published payload in `actions/cache`, keyed by the 24a-3 cache key
(`test_case_digest + prd_digest + question_set_version + model + bands`). A cache hit publishes the
cached payload without calling Jev. `BLOCKED` is not cached.

**Blocked by:** 24a-5.

**Status:** ready-for-human

- [x] The workflow restores the cache with `verify-<key>` before `run`
- [x] A cache hit skips Jev (a test uses a `SystemOne` that would fail if called)
- [x] A miss saves the payload only for non-`BLOCKED` verdicts
- [x] `actions/cache/save` is conditional on the `saved` output
- [x] A different test case, PRD, or question set misses the cache
- [x] `BLOCKED` is never written
- [x] Tests cover hit, miss, and blocked
- [x] `actionlint` passes

## Decisions / assumptions

- Actions cache is branch-scoped; no TTL.
- The cache key is the same value used as `external_id`.

## Comments

**2026-10-23 — implemented.** `verify_cache.VerdictCache` reads and writes
`.verify/cache/verdict.json`; `load(key)` owns the key match. `run` loads a matching cached payload
for READY inputs, overrides `head_sha` and `name`, and publishes without Jev. On a miss it saves the
payload unless the status is `BLOCKED`. The CLI takes `--cache-dir` and emits `saved=true|false`;
the workflow restores `verify-<key>` before `run` and saves only when `saved=true`, the key is
non-empty, and the restore was not a hit. Tests cover a hit (a `SystemOne` that fails if called), a
miss/save, `BLOCKED` (never written), a stale key, a corrupt cache, and the CLI `saved` output for
both a hit and a save. The resolver tests already cover key changes for a different test case, PRD,
or question set. 189 passed; basedpyright, lint-imports, and actionlint are green. A corrupt cache is
treated as a miss; because the Actions cache key is immutable, a persistently corrupt entry must be
deleted manually. The first live cache hit will appear on the next Test Case PR that runs twice; it
is not exercised by these tests.

**2026-10-23 — review follow-up.** `run` now validates the READY fields once, then checks the
cache, and returns `RunResult(payload, saved)`; `VerdictCache` no longer carries a `saved` flag.
Moving the cache lookup after validation also means an incomplete READY input cannot publish a
cached verdict. The model-level invariant (READY implies the three fields) is still implicit and
remains a follow-up. 189 passed; basedpyright, lint-imports, and actionlint are green.

**2026-10-23 — tracker cleanup.** All acceptance items are checked; status moved to `ready-for-human`.
