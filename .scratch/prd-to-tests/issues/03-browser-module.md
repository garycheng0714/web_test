# 03: Shared browser module

**What to build:** A single shared Python module wrapping the `playwright-cli` command, and
the existing navigation entrypoint refactored onto it without changing its observable
behavior.

**Blocked by:** 01

**Status:** wontfix

- [ ] One module owns argv construction, subprocess timeout, and output truncation for `playwright-cli`
- [ ] The module accepts an injected command runner (defaulting to the real one) and exposes a close helper
- [ ] The navigation entrypoint uses the module and still reports the page title unchanged
- [ ] A test injects a fake runner and asserts the module's behavior (argv passed, output truncated) without spawning a browser

## Comments

**Superseded (wontfix).** No shared `playwright-cli` module is introduced: the coding agent grounds
through the in-process Pydantic AI Harness `PlaywrightBrowser` capability (agent-in-ci ticket 03),
and the automation side runs in CI over a merged `test-case/<id>.md` (ADR-0006).
