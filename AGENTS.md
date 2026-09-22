# AGENTS.md

## Project
`web-test` — a Pydantic AI agent that drives a browser via `playwright-cli`.
Python 3.13, dependencies managed with `uv`. There is no `uv.lock` yet.

## Bundled skills (load before coding)
Two skills live under `.agents/skills/` — use the skill tool instead of writing from memory:
- `building-pydantic-ai-agents` — agents, tools/capabilities, structured output, streaming, testing.
- `playwright-cli` — browser automation; drives a browser via the global `playwright-cli` command.

## Commands
- Run: `uv run main.py` (`main.py` is the only entrypoint)
- Add a dependency: `uv add <pkg>` (`pydantic-ai` is already a dependency)
- `uv sync` to generate `uv.lock`
- No tests, lint, formatter, or typecheck are configured, and there is no CI.

## Gotchas
- `playwright-cli` writes snapshots, storage state, and traces to `.playwright-cli/`.
  It is gitignored and may contain credentials — never commit it or paste its contents into commits/PRs.
