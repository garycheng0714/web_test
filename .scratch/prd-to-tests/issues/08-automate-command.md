# 08: Stage 2 `automate` — approved cases to running Python tests

**What to build:** An `automate` subcommand that turns approved test cases into running
Playwright Python tests built on the Page Object Model.

**Blocked by:** 02, 03, 05, 06, 07

**Status:** wontfix

- [ ] `automate` refuses to run unless the test-case document is approved
- [ ] The automator explores the live application via `playwright-cli` to ground locators and expected values
- [ ] A dedicated snapshot cleaner turns a raw snapshot plus a case's keywords into a pruned snapshot (own module, unit-tested)
- [ ] Inspecting the test repository (list/glob/grep/read) is read-only; only the write tool mutates it
- [ ] The write guard is a pure function allowing test files, page objects, and setup files; rejecting traversal, other extensions, source files, config, and writes outside the allowed directories
- [ ] The automator reuses and extends existing page objects instead of duplicating them
- [ ] One test file is written per requirement, with priority and type emitted as test markers
- [ ] The generated tests are executed, and the browser session is closed at the end
- [ ] Agent-level tests override the model and assert the end-to-end effects (argv to the browser tool, written content, reuse, gate refusal)

## Comments

**Superseded (wontfix).** Stage 2 is no longer an `automate` subcommand over an approved document.
It is delivered by the agent-in-ci tickets: a merge-triggered workflow (06) runs
`web_test/automation/entrypoint.py` (05) over a single merged `test-case/<id>.md`, grounds with the
in-process `PlaywrightBrowser` capability (03, no `playwright-cli`), and opens a PR (02). The
qa-document gate and CLI-wrapper grounding in this ticket are gone. See ADR-0006.

Still-open pieces (tracked elsewhere): the snapshot cleaner, priority/type markers, self-heal/fixme,
and the run report.
