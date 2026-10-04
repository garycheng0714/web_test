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

Tests live in `tests/` and run under pytest with Playwright's Python bindings. The
`pytest-playwright` plugin provides the `page` fixture and defaults to chromium; pass `--headed`
to watch a run. To use another browser, install it first with `uv run playwright install firefox`
before passing `--browser firefox`. No Node/TypeScript toolchain is required.
