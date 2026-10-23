# 24a-2: Publish and update the GitHub check run

**What to build:** Extend `web_test/publishing/github.py` with a `CheckPayload` model and two
methods: `find_check_run(head_sha, *, repo, name)` and `publish_check(payload, *, repo)`. The adapter
publishes `verify-test-case` through `gh api`, updating the run that already exists on the head SHA
instead of creating a duplicate. The payload carries `name`, `head_sha`, `status: completed`,
`conclusion`, `output.title`, `output.summary`, and `external_id`.

**Blocked by:** None.

**Status:** ready-for-human

- [x] `CheckPayload` carries the fields above; `conclusion` is limited to `success`,
      `action_required`, or `failure`
- [x] `find_check_run` returns the run id for `verify-test-case` on a SHA, or `None`
- [x] `publish_check` PATCHes an existing id and POSTs when absent
- [x] The JSON body is sent through `gh api --input <temp file>`
- [x] The adapter takes `repo` as an argument; 24a-4 reads it from `GITHUB_REPOSITORY`
- [x] A fake `Runner` test covers find, POST, and PATCH
- [x] `open_pull_request` keeps its current behavior and tests
- [x] `uv run pytest`, `uv run basedpyright`, `uv run lint-imports` stay green

## Decisions / assumptions

- The verdict-to-conclusion mapping stays in 24a-4; this adapter only transports the payload.
- No new dependency: `gh` is already used by `open_pull_request`.
- The temporary JSON file is written and removed by the adapter; no credential is included.

**2026-10-21 — implemented.**

- `web_test/publishing/github.py`: `CheckConclusion`, `CheckPayload` (Pydantic boundary model),
  `GitHub.find_check_run`, and `GitHub.publish_check`. The body is posted with
  `gh api --method POST|PATCH --input <temp file>`; the temp file is removed in `finally`.
- `tests/publishing/test_github.py`: 5 new tests (find id, find none, POST body, PATCH endpoint,
  failed publish), using fakes for `Runner`; the existing `open_pull_request` tests are unchanged.
- `uv run pytest`: 143 passed, 1 skipped. `uv run basedpyright`: 0 errors, 0 warnings.
  `uv run lint-imports`: 2 contracts kept.

**2026-10-21 — transport superseded.** 24a-2b replaces the `gh api` calls with githubkit and renames
the adapter to `GitHubAdapter`. The payload, conclusion mapping, and idempotent create/update logic
are unchanged; the `Runner`-based transport is removed.

**2026-10-23 — tracker cleanup.** All acceptance items are checked; status moved to `ready-for-human`.
