# 24a-4: Build the verdict CLI

**What to build:** Give `web_test/planning/verify.py` a CLI with two modes.

- `prepare`: run 24a-3, write a plan JSON, and emit `key=` for the workflow. No Jev call.
- `run`: read the plan; publish an early outcome, or run the review with
  `typesafe_system_one` (the SDK retries HTTP failures), map the status to a conclusion, render the
  summary, and publish through `GitHubAdapter` (24a-2b).

The run exits 0 after publishing any verdict; infrastructure or publish failures exit non-zero.

**Blocked by:** 24a-2b, 24a-3.

**Status:** ready-for-agent

- [x] `prepare` writes the plan and emits `key=` to `$GITHUB_OUTPUT` (empty when no review)
- [x] `run` handles the early outcomes (0 files, more than one file, missing PRD)
- [x] `PASS` / `NEEDS_REVIEW` / `FAIL` / `BLOCKED` map to `success` / `action_required` / `failure`
- [x] The summary is `render_report(record)` and includes findings, counts, and binding digests
- [x] `BLOCKED` comes from `typesafe_system_one` (the SDK retries HTTP); empty answers and
      deterministic blocks are not retried
- [x] Publishing is idempotent through the 24a-2b adapter
- [x] A fake `SystemOne` and a fake publish callable cover the paths; no tokens in tests
- [x] Same-repo PRs only; fork handling is deferred to 24a-5
- [x] `uv run pytest`, `uv run basedpyright`, `uv run lint-imports` stay green

## Decisions / assumptions

- The workflow job stays green for verdicts; only publishing or infrastructure failures are red.
- The plan file crosses a process boundary, so it is a Pydantic model.
- The check name is `verify-test-case`; `external_id` is the cache key.
- Cache is not part of this ticket; 24a-6 adds it.
- Early outcomes publish immediately: `nothing` succeeds, `multiple` / `missing_prd` /
  `invalid` fail with a reason. The check job exits 0 once the verdict is published.

**2026-10-21 — implemented.**

- `web_test/planning/verify.py`: `PlanInput` / `Plan` (Pydantic, plan file), `prepare`, `run`,
  `_early_payload`, `_verdict_payload`, and the `prepare` / `run` CLI.
- `prepare` reads the changed-file list from a file (the workflow supplies it), resolves, writes the
  plan, and emits `key=`; it never calls Jev.
- `run` reads the plan, publishes an early outcome, or runs the review with `typesafe_system_one`,
  maps the status, renders `render_report`, and publishes through `GitHubAdapter`.
- The 4 verdicts and 4 early outcomes map as planned; `external_id` is the cache key for a review,
  and a stable label for each early outcome.
- `tests/planning/test_verify.py`: 24 tests total (10 resolver + 14 CLI/verdict). Fake `SystemOne`
  and fake publish callables; no network, tokens, or GitHub calls.
- `uv run pytest`: 171 passed, 1 skipped. `uv run basedpyright`: 0 errors, 0 warnings.
  `uv run lint-imports`: 2 contracts kept.
