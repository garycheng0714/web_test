# 24a-2: Publish and update the GitHub check run

**What to build:** Extend `web_test/publishing/github.py` with a `CheckPayload` model and two
methods: `find_check_run(head_sha)` and `publish_check(payload, head_sha)`. The adapter publishes
`verify-test-case` through `gh api`, updating the run that already exists on the head SHA instead of
creating a duplicate. The payload carries `name`, `head_sha`, `status: completed`, `conclusion`,
`output.title`, `output.summary`, and `external_id`.

**Blocked by:** None.

**Status:** ready-for-agent

- [ ] `CheckPayload` carries the fields above; `conclusion` is limited to `success`,
      `action_required`, or `failure`
- [ ] `find_check_run` returns the run id for `verify-test-case` on a SHA, or `None`
- [ ] `publish_check` PATCHes an existing id and POSTs when absent
- [ ] The JSON body is sent through `gh api --input <temp file>`
- [ ] The repository comes from `GITHUB_REPOSITORY`
- [ ] A fake `Runner` test covers find, POST, and PATCH
- [ ] `open_pull_request` keeps its current behavior and tests
- [ ] `uv run pytest`, `uv run basedpyright`, `uv run lint-imports` stay green

## Decisions / assumptions

- The verdict-to-conclusion mapping stays in 24a-4; this adapter only transports the payload.
- No new dependency: `gh` is already used by `open_pull_request`.
- The temporary JSON file is written and removed by the adapter; no credential is included.
