# 09: State setup and shared component library

**What to build:** A state-setup helper that brings the app to each case's preconditions, and
a shared component library for cross-page UI regions, both wired into the generated tests.

**Blocked by:** 08

**Status:** ready-for-agent

- [ ] Preconditions are set up through a shared helper injected via a fixture
- [ ] The helper supports API-based setup (with a UI fallback) behind one interface, so the strategy can be swapped
- [ ] The helper is unit-tested with fakes
- [ ] Shared UI regions (header, nav) are modeled as components kept in a shared component library
- [ ] Generated tests use the helper and the shared components
