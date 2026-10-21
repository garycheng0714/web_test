# AGENTS.md

## Project
`web-test` — a Pydantic AI coding agent that turns merged QA test cases into Playwright Python
tests, grounding the live page through the Pydantic AI Harness `PlaywrightBrowser` capability.
Python 3.13, dependencies managed with `uv`.

## Bundled skills (load before coding)
Skills live under `.agents/skills/` — use the skill tool instead of writing from memory. Key ones:
- `ponytail` — this repo's coding mode (full): the smallest change that fully solves the task. Auto-loaded via `opencode.json` → `instructions`; do not call the skill tool for it.
- `building-pydantic-ai-agents` — agents, tools/capabilities, structured output, streaming, testing.
- `playwright-cli` — browser automation; drives a browser via the global `playwright-cli` command.
- `qa-test-case-generation` — manual QA test-case generation from requirements/mockups/templates; vendored from `saleem-daqa/qa-test-case-generation` (not recorded in `skills-lock.json`).
- The Matt Pocock engineering flow (`ask-matt`, `to-spec`, `to-tickets`, `implement`, `tdd`, …) — configured in the `## Agent skills` section below.

**House skill libraries** (loaded at runtime via Pydantic AI Harness `Skills`) live under
`.agents/libraries/<library>/<skill>/SKILL.md`. `Skills` loads only `SKILL.md`, so a house variant
inlines any `references/` it needs. Current: `.agents/libraries/test_case_designer/qa-test-case-generation/`
(adapted from the vendored qa skill; see ADR-0005).

## Commands
- Run the navigation demo: `uv run main.py`
- Implement one merged test case: `uv run python -m web_test.automation.entrypoint --case test-case/<id>.md --workspace .`
- Test: `uv run pytest` (pytest + `pytest-playwright`; one-time `uv run playwright install chromium`)
- Add a dependency: `uv add <pkg>` (`pydantic-ai` and `pydantic-ai-harness[coder,playwright,skills]` are dependencies)
- `uv sync` to generate `uv.lock`
- No lint, formatter, or typecheck are configured. CI: `.github/workflows/ci.yml` (suite on every PR) and `.github/workflows/automate.yml` (merge-triggered automation).

## Conventions
- Boundary data — model output, config, external input — is a Pydantic `BaseModel`; it validates and serializes. Data passed between our own modules is a `@dataclass`: it is light, stores callables naturally, and needs no validation.

## Gotchas
- `playwright-cli` writes snapshots, storage state, and traces to `.playwright-cli/`.
  It is gitignored and may contain credentials — never commit it or paste its contents into commits/PRs.

## Teaching mode

This repo also serves as the human's learning workspace (`learn/`). In **planning and design**
discussions the human leads: they write the plan and make the decisions, and the agent only asks
questions, challenges, and supplies facts — no recommendations, and never write their plan.
Ticket implementation then proceeds normally. Full agreement in `learn/NOTES.md`.

## Agent skills

### Issue tracker

Issues and specs live as local markdown under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.
See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout (`CONTEXT.md` + `docs/adr/` at the repo root, created lazily).
See `docs/agents/domain.md`.
