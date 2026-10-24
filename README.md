# web-test

`web-test` is a Pydantic AI agent that reads a PRD, derives QA test cases, and generates
runnable Playwright **Python** tests. See `CONTEXT.md` for the domain glossary and `docs/adr/`
for the decisions behind it.

## Setup

Requires Python 3.13 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

One-time browser install for the Python Playwright bindings (this is separate from any
`playwright-cli` browser and only needs to be done once per machine):

```bash
uv run playwright install chromium
```

## Commands

- Run the agent: `uv run main.py`
- Run tests: `uv run pytest`
- Typecheck: `uv run basedpyright`
- Lint Python (unused imports): `uv run ruff check --select F401`
- Architecture contracts: `uv run lint-imports`
- Coverage (report only): `uv run pytest --cov=web_test --cov-report=term-missing`
- Lint workflows: `actionlint` (needs `brew install actionlint` or Docker; CI uses `rhysd/actionlint:1.7.12`)
- Add a dependency: `uv add <pkg>`
- Plan one PRD (writes `test-case/test-case-<prd-stem>.md` and opens a PR): `uv run python -m web_test.planning.entrypoint --prd prd/<name>.md --base-url https://example.com --workspace .`
- Implement one merged test case: `uv run python -m web_test.automation.entrypoint --case test-case/test-case-<prd-stem>.md --workspace .`

## Pipeline CI

`.github/workflows/ci.yml` runs on every pull request: the suite with a coverage report, a
basedpyright typecheck with a ruff unused-import lint, the import-linter architecture contracts, and
actionlint on the workflows.
The `test` job is required on `main`; `typecheck`, `contracts`, and `workflows` are shadow checks
for now. The pipeline itself is two merge-triggered workflows that mirror each other (ADR-0008):

- `plan.yml` runs when a pull request adding a `prd/**` file is **merged**: it runs the designer and
  the Jev verification record, and opens a test-case PR.
- `automate.yml` runs when a pull request adding a `test-case/**` file is **merged**: it has the coding
  agent implement its tests, and opens a PR when the suite is green. A red run (`AGENT_RED`,
  `SUITE_RED`) fails the job and keeps the deciding pytest output, suite output, trace, and generated
  files in a job summary and an `automation-evidence-<run>-<attempt>` artifact.

Both act on exactly one added file, mint a short-lived token for the `web-test-qa-flow` GitHub App
(so the PRs they open get real CI runs), and name their branch
`<kind>/<id>-<run_id>-<run_attempt>`. They need the `APP_CLIENT_ID` / `APP_PRIVATE_KEY` secrets, an
OpenCode Go model key (`OPENCODE_API_KEY`), and — for `plan` — the `WEB_TEST_BASE_URL` repository
variable. `TYPESAFE_API_KEY` is optional: without it the Jev review renders as `BLOCKED` in the PR body.

`verify.yml` runs on every pull request (opened/synchronize/reopened) and calls the shared
`verify-shared.yml` workflow. `adjudicate.yml` listens for an approving `pull_request_review` and
calls the same shared workflow with the review reason. The shared workflow resolves the changed
`test-case/**` file, runs deterministic structure checks and the Jev review, and publishes the
`verify-test-case` check on the PR head SHA: `PASS` → success, `NEEDS_REVIEW` → action_required,
`FAIL` / `BLOCKED` → failure. A structural failure is `FAIL` and is not approval-overridable. A PR
with no Test Case file reports success explicitly; more than one fails with the file list.

`verify-test-case` is required on `main` (app `web-test-qa-flow`). An approving review with a reason
re-runs `NEEDS_REVIEW` or `BLOCKED` as success for the reviewed head; `FAIL` is not overridable. A
repository admin can bypass the check as break-glass, but the reason must be recorded and the check
re-run after the fix. Both verify workflows mint the app token with `checks: write` and need
`TYPESAFE_API_KEY`.

Tests live in `tests/` and run under pytest with Playwright's Python bindings. The
`pytest-playwright` plugin provides the `page` fixture and defaults to chromium; pass `--headed`
to watch a run. To use another browser, install it first with `uv run playwright install firefox`
before passing `--browser firefox`. No Node/TypeScript toolchain is required.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `WEB_TEST_MODEL` | `openai-chat:kimi-k2.7-code` | Automation/coding-agent model (override `resolve_model()`). |
| `WEB_TEST_DESIGN_MODEL` | `openai-chat:deepseek-v4.1-flash` | Designer model (PRD → test cases; `resolve_design_model()`). |
| `GH_TOKEN` / `GITHUB_TOKEN` | — | GitHub token used by the entrypoints to open PRs and publish checks; required locally, set by CI. |
| `GITHUB_REPOSITORY` | — | `owner/repo` for the GitHub API calls; required locally, set by CI. |
| `OPENCODE_API_KEY` | — | OpenCode Go key for the OpenCode Go models above. |
| `WEB_TEST_BASE_URL` | — | Repository variable read by `plan` as the test-case `base_url`; required in CI. |
| `WEB_TEST_RUN_ID` / `WEB_TEST_RUN_ATTEMPT` | unset | Supplied by CI to make branch names run-scoped (a UTC timestamp locally). |
| `WEB_TEST_REPAIR_ATTEMPTS` | `3` | Max fix cycles for a failing suite (the automate workflow sets `10`). |
| `WEB_TEST_USAGE` | unset | Print the run's token usage and cost to stderr when set. |
| `WEB_TEST_TRACE` | unset | Print the tool-call sequence and per-request usage when set. |
| `LOGFIRE_TOKEN` | unset | Send pydantic-ai spans to Logfire; without it they print to the console. |

Debug a run's cost with the usage log:

```bash
WEB_TEST_USAGE=1 WEB_TEST_REPAIR_ATTEMPTS=10 \
uv run python -m web_test.automation.entrypoint --case test-case/test-case-<prd-stem>.md --workspace .
```

## Models

Model runs with cost/quality notes: `.scratch/agent-in-ci/model-runs.md`.

