# 01: Playwright TypeScript workspace

**What to build:** A minimal, runnable Playwright TypeScript workspace in the repo, so
that `npx playwright test` works out of the box. A developer can install dependencies,
download the Chromium browser once, and see a trivial smoke test pass.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] A `package.json` declares the Playwright test runner as a dev dependency and a `test` script
- [ ] A `playwright.config.ts` points at the tests directory and defines a Chromium project
- [ ] A trivial smoke spec exists and passes via `npx playwright test`
- [ ] Node build/test artifacts (`node_modules/`, the HTML report, test results) are gitignored
- [ ] The one-time browser download step is documented where commands are documented
