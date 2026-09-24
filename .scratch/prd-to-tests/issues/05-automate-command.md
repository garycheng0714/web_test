# 05: Stage 2 `automate` — approved cases to running tests

**What to build:** An `automate` subcommand that turns approved test cases into running
Playwright tests built on the Page Object Model. Running it on the sample PRD's approved
cases produces specs that pass.

**Blocked by:** 03, 04

**Status:** ready-for-agent

- [ ] `automate` refuses to run unless the test-case document is marked approved
- [ ] The automator explores the live application via `playwright-cli` to ground locators and expected values
- [ ] One `.spec.ts` is written per requirement, with tests grouped by case and priority/type emitted as tags
- [ ] Generated locators are encapsulated in page objects; the automator reuses and extends existing page objects instead of duplicating them
- [ ] Generated files are written only through the write guard
- [ ] The generated tests are executed with the HTML report suppressed, and the browser session is closed at the end
- [ ] Agent-level tests override the model and assert the end-to-end effects (argv to the browser tool, spec and page-object content, reuse of an existing page object, gate refusal)
