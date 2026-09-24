# 04: Page Object Model scaffold, fixture, and write guard

**What to build:** The test architecture the automator will generate into. A developer can
run a smoke spec that drives the app through a page object injected by a fixture, and the
automator's file-write guard allows exactly the generated-artifact paths.

**Blocked by:** 01, 02

**Status:** ready-for-agent

- [ ] A base page object and one canonical example page object are checked in as the house pattern
- [ ] A Playwright fixture injects page objects into tests
- [ ] Locators are encapsulated in page objects; assertions live in tests (the example demonstrates both)
- [ ] A smoke spec uses the page object via the fixture and passes
- [ ] The file-write guard is a pure function that accepts spec files under the tests directory (`.spec.ts`), page objects under the pages directory, and the fixtures file
- [ ] The guard rejects path traversal, other extensions, source files, config, and writes outside the allowed directories
- [ ] Unit tests cover both the allowed and rejected cases
