# 02: Page Object Model scaffold

**What to build:** The Page Object Model scaffold the automator will generate into: a base
page, one canonical example page object, and a fixture that injects page objects. A developer
can run a smoke test that drives the app through a page object.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] A base page and one canonical example page object are checked in as the house pattern
- [ ] Locators are encapsulated in page objects; assertions live in the tests (the example demonstrates both)
- [ ] Page objects expose actions and state queries
- [ ] A fixture injects page objects into tests
- [ ] A smoke test uses the page object via the fixture and passes
