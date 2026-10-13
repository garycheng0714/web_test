# PRD → Test Cases → Automated Tests — Spec

Status: ready-for-agent

> **Revised (ADR-0006).** The gate is now the **merge** of a PR that adds a `test-case/<id>.md`
> file (one case per file), and the automation side runs in CI, triggered by that merge (no manual
> `automate` call, no `approval` front-matter). Grounding uses the in-process Pydantic AI Harness
> `PlaywrightBrowser` capability, not `playwright-cli`. The `plan`→PR rewrite is tracked in
> `issues/06-plan-cli.md` and is not yet implemented; the user stories below keep their intent.

## Problem Statement

The builder is a test engineer who knows the QA workflow deeply: reading a PRD, deriving
test cases, deciding what to automate, and writing Playwright tests. Two things are true at
once. The pipeline is manual and slow, and much of it is worth automating. And if an agent
does all of it, the builder loses the very practice that keeps the skill sharp.

The real problem is therefore bigger than "automate QA": it is **learning how to bring a
domain into an agent**, using QA as the practice domain, and ending up with a QA agent that
genuinely works. Today the pipeline is manual and inconsistent, generated tests inline
selectors and rot, and there is no good way to encode a domain into an agent without either
hand-writing everything or blindly delegating to it.

## Solution

Build a QA automation agent as the vehicle, and learn how to build it by doing:

1. **Plan** — the agent reads a PRD and, acting as a QA engineer, derives structured test
   cases (happy, negative/validation, boundary/equivalence), traceable to requirements, and
   opens a PR that adds one `test-case/<id>.md` per case (front-matter ids and base URL).
2. **Human review gate** — the builder reviews and merges that PR; the merge is the approval.
3. **Automate** — the merge triggers a CI run: the coding agent turns the case into a runnable
   Playwright **Python** test on the Page Object Model, explores the live application to ground
   locators and expected values, runs the tests, and opens a PR when green.

**Learning method (not a product feature).** The builder stays the one doing the thinking:
OpenCode acts as a Socratic coach that asks questions and gives reasoned feedback *after*
the builder acts, never handing over answers or code. QA is the practice domain; the
transferable outcome is the experience of bringing a domain into an agent, plus a reusable
template. See `learn/MISSION.md`.

## User Stories

1. As a QA engineer, I want to point the tool at a PRD file, so that I do not have to re-read and translate it by hand.
2. As a QA engineer, I want the PRD read as plain markdown or text, so that any team's PRD format works.
3. As a QA engineer, I want the tool to act with QA discipline and derive test cases rather than echo the PRD, so that the output is genuinely test coverage.
4. As a QA engineer, I want each requirement to yield a happy-path case, so that the primary behavior is covered.
5. As a QA engineer, I want negative and validation cases, so that error handling is covered.
6. As a QA engineer, I want boundary and equivalence-partition cases, so that edge values are covered.
7. As a QA engineer, I want every test case to reference the requirement(s) it came from, so that coverage is auditable.
8. As a QA engineer, I want requirement IDs assigned automatically when the PRD lacks them, so that traceability works regardless of PRD quality.
9. As a QA engineer, I want a requirement-to-test-case mapping, so that I can see which requirements are covered.
10. As a QA engineer, I want duplicate scenarios merged across requirements while keeping all source requirement references, so that the suite is not padded.
11. As a QA engineer, I want cases prioritized and typed with constrained values, so that the suite is filterable and legible.
12. As a QA engineer, I want each case to declare its preconditions, so that setup is explicit.
13. As a QA engineer, I want each case's steps written as clear, executable steps, so that a manual QA engineer can run them.
14. As a QA engineer, I want each test case as its own markdown file, so that I can review and edit it before automation.
15. As a QA engineer, I want automation to start only after I merge the test-case PR, so that no test is generated from unreviewed cases.
16. As a QA engineer, I want approval to be the merge of the test-case PR, so that the gate is explicit in version control.
17. As a QA engineer, I want the base URL declared in each test-case file, so that a case targets its application.
18. As a QA engineer, I want each approved case turned into a runnable Playwright Python test, so that I do not hand-write it.
19. As a QA engineer, I want the automation stage to explore the live app, so that locators and expected values match reality.
20. As a QA engineer, I want the agent to reuse and extend existing page objects instead of duplicating them, so that the suite does not fork.
21. As a QA engineer, I want locators encapsulated in page objects and shared UI regions (header, nav) modeled as reusable components, so that a change is a one-place edit.
22. As a QA engineer, I want page objects to expose actions and state queries (plus an `expect_loaded()` readiness check), with test-specific assertions living in the tests, so that page objects stay reusable and specs stay readable.
23. As a QA engineer, I want preconditions set up through a shared setup helper (API where possible), so that tests start from a known state without slow UI setup.
24. As a QA engineer, I want generated tests grouped one file per requirement, so that files map cleanly to coverage.
25. As a QA engineer, I want to filter generated tests by priority and type, so that I can run a subset.
26. As a QA engineer, I want the automation stage to run the generated tests, so that output is verified, not assumed.
27. As a QA engineer, I want failing tests diagnosed and repaired automatically within a bound, so that first-pass failures do not block me.
28. As a QA engineer, I want cases that cannot be automated marked with a visible fixme and a reason, so that nothing is silently skipped.
29. As a QA engineer, I want a run report listing generated files, pass/fail, and fixme'd cases, so that I can act immediately.
30. As a developer, I want the browser session closed at the end of a run, so that no stale process lingers.
31. As a maintainer, I want the two stages as separate agents/modules, so that each has a focused prompt and can be tested alone.
32. As a maintainer, I want the Page Object conventions encoded as short rules plus a checked-in example, so that generated tests match a house style without always-loaded bloat.
33. As a maintainer, I want every module unit-testable, so that each seam is verified directly.
34. As a maintainer, I want the git/gh command runner injectable, so that tests never touch a real repository.
35. As a maintainer, I want the file-write guard to be a pure function, so that the allowed-and-rejected paths are unit-tested directly.
36. As a maintainer, I want the state-setup helper to be its own module, so that it can be swapped between API and UI setup.
37. As a maintainer, I want the snapshot-cleaning step to be its own module, so that its selection rule is testable.
38. As a maintainer, I want the existing navigation entrypoint to keep working, so that this feature is additive.
39. As a maintainer, I want the model configurable via environment variable, so that I can trade cost against quality.
40. As the builder, I want OpenCode to coach me Socratically (ask before telling), so that I stay the one reasoning about the design.
41. As the builder, I want the end result to double as a reusable template, so that the "domain → agent" learning transfers to my next domain.

## Implementation Decisions

**Pipeline shape.** An artifact hand-off, not one CLI with a gate flag. `plan` (PRD → one
`test-case/<id>.md` per case) opens a PR; **merging it is the Gate**; the merge triggers the
automation workflow, which runs the entrypoint on the merged file and opens a test PR when green.
There is no `approval` state and no `automate` argument that refuses unreviewed cases.

**Where it runs.** The automation side runs in CI (GitHub Actions), because the Gate is a GitHub
merge. `plan` may run locally. The earlier "local CLI only" framing is superseded.

**PRD input.** A required `--prd <path>` argument, read as markdown or plain text. Images,
docx, PDF, and URLs are out of scope. A small sample PRD is checked in for acceptance. The PRD
has no base-URL field; the **base URL lives in each test-case file's front-matter** (`base_url`).

**Agent harness.** Use Pydantic AI Harness capabilities as the backbone (ADR-0004): `Skills` loads
skill instructions on demand; delegation is allowed. The first stage is a single agent (ADR-0005).

**Module — Test Case designer.** A single Pydantic AI agent that reads the PRD text and produces
the test-case document. It loads the `qa-test-case-generation` skill through Pydantic AI Harness
`Skills` (a deferred capability the model loads with `load_capability`) and returns a structured
`QaReport` (ticket 06 renders each case to its own `test-case/<id>.md`). Coverage policy: for each
requirement, one case per
*applicable* technique (happy, negative/validation, boundary/equivalence); no padding. It records
`requirement_ids` for traceability, and merges duplicate scenarios while keeping every source
requirement id. There is no separate PRD parsing module.

**Test-case artifact.** One file per case at `test-case/test-case-<id>.md`, with YAML front-matter:
required `id` and `base_url`; optional `requirement_ids`, `priority`, `test_type`. The body is the
human-reviewable case (scenario, steps, expected result). Merging the PR that adds the file is the
Gate; the workflow acts on exactly the newly added file.

**Module — Test automator.** A Pydantic AI coding agent (`web_test/automation/coding_agent.py`) that
takes one merged case and produces Playwright **Python** tests. Its capabilities are the Harness
`Coder` (file/shell tools), the write guard, `Skills`, and `PlaywrightBrowser` (grounding). Its
instructions encode the workflow: load the page-object-model skill → inspect the repo → ground the
pages live via the browser capability → write/reuse page objects and tests → run `uv run pytest` →
repair on failure (bounded) → when green, load the `pr` skill and emit the PR body as
`AutomationResult.pr_body`. Non-automatable cases become a visible fixme with a reason.

**Module — Snapshot cleaner.** Before grounding, a dedicated step turns a raw page snapshot
plus a case's keywords into a pruned snapshot (only the relevant nodes). It is its own
module so its selection rule is unit-testable.

**Module — State setup.** Preconditions are set up through a shared helper (API where the app
exposes one, UI otherwise), injected into tests via a fixture. It is its own module so the
API and UI strategies can be swapped.

**Test architecture — Page Object Model (Python).**
- Locators are encapsulated inside page objects; selectors are not exposed to tests.
- Page objects expose actions and state queries; **test-specific assertions live in the tests**.
  Each page object may additionally own an `expect_loaded()` readiness check that verifies its own
  URL plus content unique to that page — never shared chrome (header/nav/footer). `expect_loaded()`
  returns the page so same-page calls chain (optionally across lines inside parentheses).
- Shared UI regions (header, nav) are modeled as **components** kept in a **shared component
  library**, reused across features. A component owns the actions on its own elements (e.g.
  `Header.click_nav_link`), with pages delegating to them; tests never reach through a component
  to click.
- Action catalog is **per feature**: only elements along the approved cases' paths become
  actions, so no unused actions accumulate; shared components are the exception and live in
  the shared library.
- The automator must reuse and extend existing page objects before creating new ones.

**Write guard.** The file-write tool accepts only generated test artifacts: Python test files
under the tests directory, page objects under the pages directory, and the fixtures/setup
files. Everything else (traversal, source files, config, other extensions) is rejected. The
guard is a pure function.

**Shared browser module (superseded).** The earlier plan to wrap the external `playwright-cli` in a
shared module is dropped; grounding goes through the in-process `PlaywrightBrowser` capability
(ADR-0006).

**Grounding (revised).** Grounding uses the `PlaywrightBrowser` capability: `navigate` then
`snapshot` returns an accessibility tree with `aria-ref` handles to target. The `playwright-cli`
TypeScript-to-Python translation gap no longer applies.

**Model.** Default to a stronger model for the reasoning stages, configurable via environment
variable.

**Python test workspace.** Tests run under pytest with Playwright's Python bindings. No Node
workspace is required.

**Agent instructions** are written as prose rules, not code, per `writing-for-agents`.

## Testing Decisions

- A good test verifies external behavior through a public interface and survives refactors;
  it does not assert on internals.
- **Every module is unit-tested at its seam**, with external dependencies injected.
- **Primary seam — Test Case designer.** Tests override the model with a Pydantic AI test
  model, then assert the produced structured `QaReport` (coverage, traceability via
  `requirement_ids`, dedup, ids). No network. The `qa-test-case-generation` skill is loaded via
  harness `Skills` from `.agents/libraries/`.
- **Primary seam — Test automator.** Tests override the model to script tool calls, then assert
  the end-to-end effects: the grounding tools are attached, page-object/test content is written,
  an existing page object is reused rather than duplicated, a failing run triggers repair, and
  unautomatable cases become fixme. Unit tests spawn no browser or network; the browser toolset is
  exercised against the SUT in its own tests.
- **Entrypoint seam.** `automate` takes injected `agent`, `git`, `pr`, and `suite`; tests inject
  fakes and assert the `AutomationOutcome`
  (`published`/`agent_red`/`suite_red`/`no_changes`/`failed`).
- **Secondary seam — write guard**, a pure function: accepts test files, page objects, and
  setup files; rejects traversal, other extensions, source files, config, and writes outside
  the allowed directories.
- **Secondary seam — snapshot cleaner**, a pure function: given a raw snapshot and a case's
  keywords, keeps only the relevant nodes.
- **Secondary seam — state setup**: asserted with a fake API/UI adapter.
- The command runner is injected so no seam runs real git/gh in tests.
- Prior art: the suite under `tests/`.

## Out of Scope

- Other delivery forms — an MCP server or a long-running service; the automation side runs as a
  merge-triggered CI job.
- Delegating code edits to an existing coding agent (see ADR-0001).
- PRD formats other than markdown/plain text: images, docx, PDF, URL.
- A PR review gate after automation; only the test-case review gate exists in v1.
- Non-functional test design (accessibility, performance, security).
- A BDD execution runtime — cases are translated to plain Playwright Python tests.
- Fan-out (one agent per requirement) — the stages process the whole PRD.
- Authenticated multi-page journeys beyond what the automator can discover.

## Further Notes

- **Two levels.** This spec describes the *product* (the QA automation agent). The *project's*
  real goal — learning how to bring a domain into an agent — lives in `learn/MISSION.md`;
  the Socratic coaching is the learning method, not a product feature.
- This spec supersedes the earlier `playwright-test-generator` spec, which covered only the
  automation stage and mis-stated the problem, and the earlier TypeScript direction.
- First automation run requires a one-time browser install for Playwright's Python bindings.
- The `PlaywrightBrowser` capability starts Chromium on the first tool call and closes it when the
  run ends; a run that never browses never launches one.
- **Resolved:** the standalone PRD parsing step was dropped; the first stage is a single agent
  (`PRD text → QaReport`) that loads the `qa-test-case-generation` skill via harness `Skills`
  (ADR-0005). The base URL lives in each test-case file's front-matter, not the PRD.
