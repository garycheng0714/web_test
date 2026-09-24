# 02: Shared browser module, pytest scaffold, navigation refactor

**What to build:** A single shared Python module that wraps the `playwright-cli` command,
plus the repo's first Python test framework. The existing navigation entrypoint is
refactored onto the shared module without changing its observable behavior.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] One module owns argv construction, subprocess timeout, and output truncation for `playwright-cli`
- [ ] The module accepts an injected command runner (defaulting to the real one) and exposes a close helper
- [ ] The navigation entrypoint uses the shared module and still reports the page title unchanged
- [ ] pytest is configured for the repo
- [ ] A test injects a fake runner and asserts the module's behavior (argv passed, output truncated) without spawning a browser
