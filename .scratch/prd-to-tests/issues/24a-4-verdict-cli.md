# 24a-4: Build the verdict CLI

**What to build:** Give `web_test/planning/verify.py` a CLI with two modes.

- `prepare`: run 24a-3, write a plan JSON, and emit `key=` / `early=` for the workflow. No Jev call.
- `run`: read the plan; publish an early outcome, or run the review with
  `typesafe_system_one` (the SDK retries HTTP failures), map the status to a conclusion, render the
  summary, and publish through 24a-2.

The run exits 0 after publishing any verdict; infrastructure or publish failures exit non-zero.

**Blocked by:** 24a-1, 24a-2, 24a-3.

**Status:** ready-for-agent

- [ ] `prepare` writes the plan and emits `key=` / `early=` to `$GITHUB_OUTPUT`
- [ ] `run` handles the early outcomes (0 files, more than one file, missing PRD)
- [ ] `PASS` / `NEEDS_REVIEW` / `FAIL` / `BLOCKED` map to `success` / `action_required` / `failure`
- [ ] The summary is `render_report(record)` and includes findings, counts, and binding digests
- [ ] `BLOCKED` comes from `typesafe_system_one` (the SDK retries HTTP); empty answers and
      deterministic blocks are not retried
- [ ] Publishing is idempotent through the 24a-2 adapter
- [ ] A fake `SystemOne` and a fake `Runner` cover the publish paths; no tokens in tests
- [ ] Same-repo PRs only; a fork PR is reported as unsupported
- [ ] `uv run pytest`, `uv run basedpyright`, `uv run lint-imports` stay green

## Decisions / assumptions

- The workflow job stays green for verdicts; only publishing or infrastructure failures are red.
- The plan file crosses a process boundary, so it is a Pydantic model.
- The check name is `verify-test-case`; `external_id` is the cache key.
- Cache is not part of this ticket; 24a-6 adds it.
