# 03: Shared browser module

**What to build:** A single shared Python module wrapping the `playwright-cli` command, and
the existing navigation entrypoint refactored onto it without changing its observable
behavior.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] One module owns argv construction, subprocess timeout, and output truncation for `playwright-cli`
- [ ] The module accepts an injected command runner (defaulting to the real one) and exposes a close helper
- [ ] The navigation entrypoint uses the module and still reports the page title unchanged
- [ ] A test injects a fake runner and asserts the module's behavior (argv passed, output truncated) without spawning a browser
