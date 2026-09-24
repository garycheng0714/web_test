# PRD → Test Cases → Automated Tests — Spec

Status: ready-for-agent

## Problem Statement

Today, turning a product requirements document (PRD) into automated tests is a manual,
multi-step craft. A QA engineer reads the PRD, works out which test cases it implies,
decides which are worth automating, then hand-writes Playwright tests and hunts for
locators by hand. The reasoning (reading requirements as a QA, choosing test cases) and
the mechanical work (writing and verifying tests) are tangled together, so the whole
pipeline is slow and inconsistent. The generated tests also tend to inline selectors,
so they rot quickly and repeat themselves across specs.

## Solution

A command-line tool that runs the pipeline in clearly separated stages:

1. **Plan** — read a PRD and, acting as a QA engineer, derive structured test cases
   (happy path, negative/validation, boundary/equivalence), each traceable to a PRD
   requirement, written to a human-reviewable markdown file.
2. **Human review gate** — the user reviews and edits the test cases and approves them.
3. **Automate** — turn each approved test case into a runnable Playwright TypeScript
   test built on the Page Object Model, exploring the live application via
   `playwright-cli` to ground locators and expected values, then run the tests and
   self-heal failures.

The reasoning stage and the automation stage are deliberately separate so each can be
verified on its own, and so the QA judgement is reviewable before any code is generated.

## User Stories

1. As a QA engineer, I want to point the tool at a PRD file, so that I do not have to re-read and translate it by hand.
2. As a QA engineer, I want the PRD read as plain markdown or text, so that any team's PRD format works.
3. As a QA engineer, I want the tool to act with QA discipline and derive test cases rather than echo the PRD, so that the output is genuinely test coverage.
4. As a QA engineer, I want each requirement to yield a happy-path case, so that the primary behavior is covered.
5. As a QA engineer, I want negative and validation cases, so that error handling is covered.
6. As a QA engineer, I want boundary and equivalence-partition cases, so that edge values are covered.
7. As a QA engineer, I want every test case to reference the requirement it came from, so that coverage is auditable.
8. As a QA engineer, I want requirement IDs assigned automatically when the PRD lacks them, so that traceability works regardless of PRD quality.
9. As a QA engineer, I want a requirement-to-test-case mapping, so that I can see which requirements are covered.
10. As a QA engineer, I want duplicate scenarios merged across requirements while keeping all source requirement references, so that the suite is not padded.
11. As a QA engineer, I want cases prioritized (P1–P3), so that I can run the important ones first.
12. As a QA engineer, I want each case classified by type (happy/negative/boundary), so that the suite is legible.
13. As a QA engineer, I want the test cases written in Given/When/Then phrasing, so that they read as behavior.
14. As a QA engineer, I want the test cases as a structured markdown file, so that I can review and edit them before automation.
15. As a QA engineer, I want the pipeline to stop after planning until I approve, so that no test is generated from unreviewed cases.
16. As a QA engineer, I want approval expressed as a simple state in the test-case file, so that the gate is explicit and auditable.
17. As a QA engineer, I want to re-run planning after editing the PRD without losing control of the output, so that the workflow is iterative.
18. As a QA engineer, I want the application base URL taken from the PRD but overridable on the command line, so that I can target different environments.
19. As a QA engineer, I want each approved case turned into a runnable Playwright test, so that I do not hand-write it.
20. As a QA engineer, I want the automation stage to explore the live app via playwright-cli, so that locators and expected values match reality.
21. As a QA engineer, I want generated tests to use semantic, role-based locators, so that they survive minor changes.
22. As a QA engineer, I want generated locators encapsulated in page objects, so that a selector change is a one-place edit.
23. As a QA engineer, I want page objects to expose actions and queries, with assertions living in the tests, so that page objects stay reusable and specs stay readable.
24. As a QA engineer, I want the automator to reuse and extend existing page objects instead of duplicating them, so that the suite does not fork.
25. As a QA engineer, I want generated tests grouped one file per requirement, so that files map cleanly to coverage.
26. As a QA engineer, I want priority and type emitted as Playwright tags, so that I can filter runs.
27. As a QA engineer, I want the automation stage to run the generated tests, so that output is verified, not assumed.
28. As a QA engineer, I want failing tests diagnosed and repaired automatically within a bound, so that first-pass failures do not block me.
29. As a QA engineer, I want cases that cannot be automated marked with a visible fixme and a reason, so that nothing is silently skipped.
30. As a QA engineer, I want a run report listing generated files, pass/fail, and fixme'd cases, so that I can act immediately.
31. As a developer, I want the browser session closed at the end of a run, so that no stale process lingers.
32. As a maintainer, I want the two stages as separate agents, so that each has a focused prompt and can be tested alone.
33. As a maintainer, I want the Page Object conventions encoded as short rules plus a checked-in example, so that generated tests match a house style without always-loaded bloat.
34. As a maintainer, I want a minimal Playwright TypeScript workspace in the repo, so that tests run out of the box.
35. As a maintainer, I want the command runner injectable, so that tests run without spawning a browser.
36. As a maintainer, I want the file-write guard to be a pure function, so that the allowed-and-rejected paths are unit-tested directly.
37. As a maintainer, I want the agent's tool wiring testable via Pydantic AI test models, so that the seams are verified deterministically.
38. As a maintainer, I want the existing navigation entrypoint to keep working, so that this feature is additive.
39. As a maintainer, I want the model configurable via environment variable, so that I can trade cost against quality.
40. As a learner, I want this built through the Matt Pocock flow (spec → tickets → implement), so that the process is practiced, not just read.

## Implementation Decisions

**Pipeline shape.** Two stages with a human gate between, exposed as one CLI with two
subcommands: `plan` (PRD → test cases) and `automate` (test cases → Playwright tests).
`automate` refuses to run unless the test-case file is marked approved. Review is a state
in the artifact, not a separate service.

**Stage 1 — QA test designer.** A Pydantic AI agent whose input is the PRD text and whose
output is the structured test-case document. It applies a fixed coverage policy: for each
requirement, one case per *applicable* technique (happy, negative/validation,
boundary/equivalence); it does not pad. It assigns stable requirement IDs when absent and
maintains a requirement→case mapping. It merges duplicate scenarios across requirements,
keeping every source requirement reference.

**Test-case artifact.** A single structured markdown document per feature, carrying
front-matter for the base URL and an approval state, a requirement→case mapping, and one
entry per case with: id, source requirement id(s), priority (P1–P3), type
(happy/negative/boundary), preconditions, Given/When/Then steps, and expected result.
It lives with the feature's planning artifacts under the local tracker convention.

**Stage 2 — Test automator.** A Pydantic AI agent that consumes the approved cases and
produces Playwright TypeScript. It has function tools to: run a `playwright-cli` command
from an argv list (returning stdout/stderr), write a generated artifact (see the write
guard below), read a test back, and run a Playwright test with the HTML report suppressed.
Its instructions encode the workflow: explore → write page objects and specs → run →
diagnose and repair on failure, bounded to a small number of attempts. One `.spec.ts` per
requirement, tests grouped by case; priority and type become tags; non-automatable cases
become `test.fixme` with a reason and are listed in the report.

**Test architecture — Page Object Model.** Generated tests follow a classic POM shape:

- Locators are encapsulated inside page objects; selectors are not exposed to tests.
- Page objects expose actions and queries; **assertions live in the tests**, not the page
  objects.
- Granularity is one page object per application page, with component objects only when a
  region is genuinely reused.
- A Playwright fixture injects page objects into tests.
- The automator must **reuse and extend existing page objects** before creating new ones;
  it never duplicates a page object across specs.

The conventions are delivered to the automator as short rules in its instructions plus a
checked-in canonical example (a base page, one page object, and the fixture) the agent
imitates. If the rules grow, they are disclosed to a referenced document rather than inlined.

**Write guard.** The file-write tool accepts only paths that are generated test artifacts:
spec files under the tests directory ending in `.spec.ts`, page objects under the pages
directory, and the fixtures file. Everything else (traversal, source files, config, other
extensions) is rejected. The guard is a pure function.

**Shared browser module.** A single deep module wraps `playwright-cli`: it owns argv
construction, timeouts, and output truncation, and it **accepts an injected command
runner** so tests can substitute a fake. It also exposes a close helper. The navigation
entrypoint is refactored to use the same module.

**Model.** Default to a stronger model for both stages (a Google model, chosen over the
lightweight one because both reasoning and code generation are demanded), configurable via
environment variable.

**Node workspace.** A minimal Playwright TypeScript workspace: a `package.json` with the
Playwright test runner as a dev dependency and a test script, and a `playwright.config.ts`
with the tests directory and a Chromium project. Node build/test artifacts are gitignored.

**Python test framework.** Python tests use pytest.

**Self-heal bound.** At most three repair attempts before reporting failure.

**PRD interface.** A required `--prd <path>` argument. A small sample PRD is checked in for
acceptance and practice. The base URL is a PRD field; a command-line override exists.

**Agent instructions** are written as prose rules, not code, per `writing-for-agents`.

## Testing Decisions

- A good test verifies external behavior through a public interface and survives
  refactors; it does not assert on internals.
- **Primary seam — the Stage 1 agent's public interface.** Tests override the model with a
  Pydantic AI test model to script the LLM, then assert the produced test-case document:
  coverage per requirement, traceability, dedup, IDs, and the approval gate. No network.
- **Primary seam — the Stage 2 agent's public interface.** Tests override the model to
  script tool calls, then assert the end-to-end effects: correct argv reaches the browser
  tool, correct spec and page-object content is written, an existing page object is reused
  rather than duplicated, a failing run triggers repair, and unautomatable cases become
  fixme. No browser or network.
- **Secondary seam — the write guard**, a pure function: accepts `tests/*.spec.ts`,
  `pages/**`, and the fixtures file; rejects traversal, other extensions, source files,
  config, and writes outside the allowed directories.
- **Secondary seam — the CLI gate**: `automate` refuses unreviewed cases.
- The command runner is injected so no seam spawns `playwright-cli`.
- Prior art: none — this repo has no test suite yet; this feature introduces the first
  Python tests (pytest), the first Playwright workspace, and the first POM layer.

## Out of Scope

- PRD formats other than markdown/plain text (no docx, PDF, or URL ingestion).
- Non-functional test design (accessibility, performance, security).
- A BDD execution runtime — test cases are translated to plain Playwright tests, not run
  as Cucumber/`.feature` files.
- Component-object granularity beyond genuinely reused regions.
- CI integration or an automated pipeline.
- Multiple-model routing or per-stage cost optimization.
- An interactive/conversational REPL.
- Fan-out (one agent per requirement) — the stages process the whole PRD.
- Authenticated multi-page journeys beyond what the automator can discover.

## Further Notes

- This spec supersedes the earlier `playwright-test-generator` spec, which covered only
  the automation stage and mis-stated the problem.
- The Page Object conventions are deliberately not a skill: the Stage 2 automator is a
  standalone Pydantic AI agent that does not load the coding agent's skill directory, so
  the conventions live in its instructions plus a checked-in example.
- First automation run requires a one-time browser download (`npx playwright install
  chromium`); it is an environment change, not a code change.
- The chosen default model may need revisiting; the repair loop and the human review gate
  are the mitigation for weak generation.
- `playwright-cli` keeps a shared default browser session across invocations, so
  exploration commands compose naturally; the session is closed at the end of a run.
