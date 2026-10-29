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
- Designer eval units (local Phoenix): `PYTHONPATH=. uv run --group eval python .scratch/designer-evals/run_eval.py`
- Export designer labels: `PYTHONPATH=. uv run --group eval python .scratch/designer-evals/export_labels.py --run <run>`
- Designer eval report: `PYTHONPATH=. uv run --group eval python .scratch/designer-evals/report.py --run <run>`
- Test: `uv run pytest` (pytest + `pytest-playwright`; one-time `uv run playwright install chromium`)
- Typecheck: `uv run basedpyright` (scope: `web_test`, `standard` mode)
- Lint Python (unused imports): `uv run ruff check --select F401`
- Architecture contracts: `uv run lint-imports`
- Coverage (report only): `uv run pytest --cov=web_test --cov-report=term-missing`
- Add a dependency: `uv add <pkg>` (`pydantic-ai` and `pydantic-ai-harness[coder,playwright,skills]` are dependencies)
- `uv sync` to generate `uv.lock`
- No Python formatter is configured; workflows are checked with `actionlint` in CI. CI: `.github/workflows/ci.yml` (suite with coverage, typecheck with lint, contracts, workflows on every PR) and `.github/workflows/automate.yml` (merge-triggered automation).

## Language
Reply in Traditional Chinese. Keep code, commit messages, and existing English docs in their
current language; do not translate them.

## Conventions
- Boundary data — model output, config, external input — is a Pydantic `BaseModel`; it validates and serializes. Data passed between our own modules is a `@dataclass`: it is light, stores callables naturally, and needs no validation.

## Diagrams

When a flow has three or more steps, calls, or decisions, show it as a vertical ASCII/Unicode
diagram (`│`, `▼`, `──>`) instead of a prose list. This applies to replies, plans, and tickets; PRDs
and skills keep their Mermaid diagrams. Use English labels, do not mix CJK text with box-drawing
characters in the same row, and keep the rows aligned in Ghostty.

```text
PR event
  │
  ▼
checkout head SHA
  │
  ▼
publish check
```

## Refactoring
- Split by responsibility, not by line count. A helper needs a named phase; do not create one function per numbered step.
- A responsibility is one reason to change plus one contract (its input/output type or the
  external boundary it faces). Two parts are separate responsibilities when a plausible change edits
  only one of them, and one can be understood and tested without importing the other. Code that
  always changes together, shares one type, and has no independent test is one responsibility.
- Keep dependency arrows pointing from composition roots and use cases toward shared schemas. Shared schemas must not import review or automation modules.
- Shared modules (`web_test.planning.schema`, `web_test.publishing`) are leaves; see
  `docs/adr/0009-shared-modules-are-leaves.md`. `uv run lint-imports` enforces the direction.
- Put cross-type conversion in the composition root or an adapter, not as a method on either data model.
- Name by role and domain language; check `CONTEXT.md` first and avoid overloading existing terms.
- Internal closed sets use `StrEnum`; otherwise follow the boundary/internal data convention above.
- A responsibility with its own contract and change reason may become a module even with one caller. Otherwise, do not add a module until there is a second caller or a second variation.
- A pure refactor keeps behavior: run the full suite and verify any version or digest that must not change. Test through real entry points; do not add test-only production helpers.
- Before a ticket that adds or moves a boundary type, record its `Shape` in the ticket: types, boundary, invariants. For a new module, include the six-line module plan.

### Module planning

Before adding or splitting a module, answer these six lines in the plan (skip for a trivial
single-file change):

1. Input
2. Output
3. External boundaries (API, file, CI)
4. Domain types vs adapters
5. Single-variation parts to leave alone
6. Responsibilities: which change reasons and contracts will this module serve?

## Review

- Label each code-review finding `behavior` or `polish`.
- Fix `behavior` in the current ticket. Open a ticket for `polish`; do not expand the current change.

## Gotchas
- `playwright-cli` writes snapshots, storage state, and traces to `.playwright-cli/`.
  It is gitignored and may contain credentials — never commit it or paste its contents into commits/PRs.

## Teaching mode

This repo also serves as the human's learning workspace (`learn/`). In **planning and design**
discussions the human leads: they write the plan and make the decisions. The agent asks questions,
challenges, and supplies facts. It may recommend only when a concrete tradeoff or risk is on the
table, and must label the recommendation with its reason. With no concrete tradeoff or risk, it
asks instead of recommending. When the user explicitly asks for a recommendation, the agent may
answer, but labels it as an answer and says whether it rests on a concrete tradeoff or risk. The
agent never writes the human's plan. Ticket implementation then proceeds normally. Full agreement
in `learn/NOTES.md`.

## Agent skills

### Issue tracker

Issues and specs live as local markdown under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.
See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout (`CONTEXT.md` + `docs/adr/` at the repo root, created lazily).
See `docs/agents/domain.md`.
