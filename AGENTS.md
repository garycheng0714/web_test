# AGENTS.md

## Project
`web-test` — a Pydantic AI agent that drives a browser via `playwright-cli`.
Python 3.13, dependencies managed with `uv`.

## Bundled skills (load before coding)
Skills live under `.agents/skills/` — use the skill tool instead of writing from memory. Key ones:
- `building-pydantic-ai-agents` — agents, tools/capabilities, structured output, streaming, testing.
- `playwright-cli` — browser automation; drives a browser via the global `playwright-cli` command.
- The Matt Pocock engineering flow (`ask-matt`, `to-spec`, `to-tickets`, `implement`, `tdd`, …) — configured in the `## Agent skills` section below.

## Commands
- Run: `uv run main.py` (`main.py` is the only entrypoint)
- Add a dependency: `uv add <pkg>` (`pydantic-ai` is already a dependency)
- `uv sync` to generate `uv.lock`
- No tests, lint, formatter, or typecheck are configured, and there is no CI.

## Gotchas
- `playwright-cli` writes snapshots, storage state, and traces to `.playwright-cli/`.
  It is gitignored and may contain credentials — never commit it or paste its contents into commits/PRs.

## Agent skills

### Issue tracker

Issues and specs live as local markdown under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.
See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout (`CONTEXT.md` + `docs/adr/` at the repo root, created lazily).
See `docs/agents/domain.md`.
