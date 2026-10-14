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
- Add a dependency: `uv add <pkg>`
- Implement one merged test case: `uv run python -m web_test.automation.entrypoint --case test-case/<id>.md --workspace .`

## Automation CI

`.github/workflows/ci.yml` runs the suite on every pull request. `.github/workflows/automate.yml`
runs when a `test-case/**` pull request is **merged**: it finds the newly added case file, has the
coding agent implement its tests, and opens a PR when the suite is green. It needs an OpenCode Go
model key secret (`OPENCODE_API_KEY`; the model defaults to `openai-chat:kimi-k2.7-code`) and the
default `GITHUB_TOKEN` (same-repo PRs only).

Tests live in `tests/` and run under pytest with Playwright's Python bindings. The
`pytest-playwright` plugin provides the `page` fixture and defaults to chromium; pass `--headed`
to watch a run. To use another browser, install it first with `uv run playwright install firefox`
before passing `--browser firefox`. No Node/TypeScript toolchain is required.
