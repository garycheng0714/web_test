# 24a-2b: Replace the gh subprocess with githubkit

**What to build:** Replace the `gh api` calls in `web_test/publishing/github.py` with the
`githubkit` SDK. Rename the adapter to `GitHubAdapter`, keep the payload and method names, read the
token and repository from the environment (fail fast), and keep the subprocess only for Git and the
test suite.

**Blocked by:** 24a-2 (the payload and the check-run calls it replaces).

**Status:** ready-for-human

- [x] Add `githubkit` as a dependency
- [x] `GitHubAdapter(client, owner, repo)` replaces the `Runner`/`workspace` adapter
- [x] `from_env()` reads `GH_TOKEN` or `GITHUB_TOKEN` and `GITHUB_REPOSITORY`; missing or malformed
      values raise `RuntimeError`
- [x] `open_pull_request` uses `client.rest.pulls.create`
- [x] `find_check_run` uses `client.rest.checks.list_for_ref`
- [x] `publish_check` uses `client.rest.checks.create` or `checks.update`, with
      `completed_at=datetime.now(UTC)`
- [x] `CheckConclusion` is a `Literal` boundary type
- [x] SDK errors become `GitHubError(RuntimeError)` with the operation, HTTP details, and
      `__cause__`
- [x] The entrypoints construct `GitHubAdapter.from_env()`
- [x] No `gh` subprocess remains under `web_test/`
- [x] Fake-client tests cover create, update, find, pull, errors, and `from_env`
- [x] `uv run pytest`, `uv run basedpyright`, `uv run lint-imports`, `uv lock --check` stay green

## Decisions / assumptions

- `githubkit` over PyGithub: fully typed, Pydantic models, sync client, aligned with the repo's
  basedpyright setup.
- Fail fast: local runs must set `GH_TOKEN`/`GITHUB_TOKEN` and `GITHUB_REPOSITORY`; CI already does.
- `owner`/`repo` live on the adapter; the check methods no longer take `repo` per call.
- `completed_at` is supplied so a PATCH after a rerun reports the new completion time.
- `PullRequest`, `CheckPayload`, and the conclusion values are unchanged in meaning.
- `Git` and `Suite` keep using `subprocess_runner`; only GitHub moved to the SDK.

## Comments

**2026-10-21 — implemented.**

- `web_test/publishing/github.py`: `GitHubAdapter`, `from_env`, `_request`/`_describe`,
  `GitHubError`; `GitHub` (ours) is gone, the SDK keeps its name. Token and repository resolution
  are separate `_token` / `_repository` helpers; `from_env` only composes them. `_CheckBody` /
  `_check_body` hold the shared check-run body; `create` and `update` only differ by the method,
  `run_id`, and the endpoint-specific `output` type.
- `publish.py`, `planning/publisher.py`, and both entrypoints use `GitHubAdapter`; the entrypoints
  build it from the environment.
- `tests/publishing/test_github.py`: 11 tests with a fake SDK client; `completed_at` is asserted as
  an aware UTC datetime.
- `uv run pytest`: 147 passed, 1 skipped. `uv run basedpyright`: 0 errors, 0 warnings.
  `uv run lint-imports`: 2 contracts kept. `uv lock --check` passes.
- `grep '"gh"' web_test` returns nothing; `subprocess_runner` remains only for `Git` and `Suite`.

**2026-10-23 — tracker cleanup.** All acceptance items are checked; status moved to `ready-for-human`.
