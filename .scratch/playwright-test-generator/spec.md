# Playwright Test Generator — Spec

Status: ready-for-agent

## Problem Statement

今天要把一句自然語言任務（例如「Go to https://automationexercise.com/ and report
the page title and URL.」）變成一個可執行的 Playwright 自動化測試，得靠人手動開瀏覽器、
找 locator、抄 playwright-cli 產出的 TypeScript、再自己補斷言。這個過程重複、容易出錯，
而且產出的測試沒有被執行驗證過。

## Solution

提供一個命令列入口，吃一句自然語言任務，產出一個 Playwright TypeScript 測試檔
（`tests/<kebab-case>.spec.ts`），並實際執行它；若失敗，agent 會診斷並自我修復，
直到測試綠燈或達重試上限。agent 透過 `playwright-cli` 探索真實頁面以取得可信的 locator
與期望值，而不是憑空生成。

## User Stories

1. As a developer, I want to pass a natural-language task on the command line, so that I get a runnable Playwright test without hand-writing it.
2. As a developer, I want the agent to explore the live page via playwright-cli, so that the generated locators match the real DOM.
3. As a developer, I want the generated test written to a predictable path under `tests/`, so that I know where to find it.
4. As a developer, I want the generated test to use semantic, role-based locators, so that it survives minor DOM changes.
5. As a developer, I want the agent to derive expected values (title, URL, text) from the live page, so that assertions are correct rather than guessed.
6. As a developer, I want the agent to run the generated test itself, so that I do not have to manually verify it.
7. As a developer, I want the agent to fix a failing test automatically, so that a first-pass failure does not block me.
8. As a developer, I want the self-heal loop bounded, so that the agent cannot spin forever.
9. As a developer, I want the agent restricted to writing test files under `tests/`, so that it cannot overwrite arbitrary repo files.
10. As a developer, I want the final summary to state the test path and pass/fail status, so that I can act on the result immediately.
11. As a developer, I want the browser session closed when the run finishes, so that no stale process lingers.
12. As a developer, I want a minimal Playwright TypeScript workspace in the repo, so that `npx playwright test` works out of the box.
13. As a maintainer, I want the agent's tool wiring testable without launching a browser, so that tests are fast and deterministic.
14. As a maintainer, I want the command runner injectable, so that tests can substitute a fake runner.
15. As a maintainer, I want the test-path guard to be a pure, unit-testable function, so that the safety rule is verified directly.
16. As a maintainer, I want the existing navigation agent to keep working, so that this feature is purely additive.
17. As a learner, I want this feature built by following the Matt Pocock flow (spec → tickets → implement), so that the process itself is practiced.

## Implementation Decisions

- A Python command-line entrypoint in addition to the existing navigation entrypoint; the navigation agent is unchanged in behavior.
- A shared `browser_tools` module is the single source for invoking `playwright-cli`. It exposes a run function that **accepts an injected command runner** (defaults to the real subprocess runner) and a close helper. This is a deep module: small interface, it owns argv construction, timeouts, and output truncation.
- The generator agent is a Pydantic AI `Agent` named for this purpose, using model `google:gemini-2.5-flash-lite`.
- The agent is given four function tools:
  - a browser tool that runs a `playwright-cli` command from an argv list and returns stdout/stderr (truncated),
  - a write-test tool that writes a test file and **rejects any path outside `tests/` or not ending in `.spec.ts`**,
  - a read-test tool to read a test back for repair,
  - a run-test tool that runs the Playwright test with the HTML report suppressed and returns the output.
- The agent's instructions encode the generate/heal workflow: explore → generate TypeScript → write file → run → diagnose and fix on failure, bounded to a small number of repair attempts.
- A minimal Playwright TypeScript workspace: a `package.json` with `@playwright/test` as a dev dependency and a `test` script, and a `playwright.config.ts` with `testDir` pointing at `tests/` using the Chromium project.
- Generated tests are committed artifacts under `tests/`.
- Node build/test artifacts (`node_modules/`, `playwright-report/`, `test-results/`) are gitignored.
- Agent instructions are written as prose rules (not code), per `writing-for-agents`.

## Testing Decisions

- A good test verifies external behavior through a public interface and survives refactors; it does not assert on internals.
- **Primary seam — the agent's public interface.** Tests override the model with Pydantic AI `FunctionModel`/`TestModel` to script tool calls deterministically, then assert the end-to-end effects: the right argv reaches the browser tool, the correct file content is written, and a failing run triggers a repair. No real browser or network.
- **Secondary seam — the write-test path guard**, tested as a pure function: accepts `tests/*.spec.ts`, rejects traversal, other extensions, and writes outside `tests/`.
- The command runner is injected so both seams can run without spawning `playwright-cli`.
- Prior art: none — this repo currently has no test suite. This feature introduces the first Python tests; the framework choice (pytest vs stdlib) is an implementation decision made in the first ticket.

## Out of Scope

- The `--debug=cli` + `playwright-cli attach` seed/fixtures workflow for apps that need login or custom setup.
- CI integration and an automated test pipeline.
- Supporting multiple model providers or letting the user pick the model at runtime.
- An interactive/conversational REPL for the generator.
- Generating multi-page or authenticated user journeys.
- Enforcing generated-test style beyond semantic-locator guidance.

## Further Notes

- First run requires a one-time browser download (`npx playwright install chromium`); this is an environment change, not a code change.
- The chosen model (`gemini-2.5-flash-lite`) may be weak at tool orchestration and TypeScript generation; clear instructions plus the bounded repair loop are the mitigation. If quality is insufficient, revisit the model.
- `playwright-cli` keeps a shared default browser session across separate invocations, so exploration commands (`open`, `snapshot`, `eval`) compose naturally; the session is closed at the end of a run.
