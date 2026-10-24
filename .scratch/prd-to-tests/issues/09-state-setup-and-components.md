# 09: State setup and shared component library

**What to build:** A state-setup helper that brings the app to each case's preconditions, and
a shared component library for cross-page UI regions, both wired into the generated tests.

**Blocked by:** None (agent-in-ci 05/06 complete; re-scope after ADR-0006/0007).

**Status:** needs-triage

- [ ] Preconditions are set up through a shared helper injected via a fixture
- [ ] The helper supports API-based setup (with a UI fallback) behind one interface, so the strategy can be swapped
- [ ] The helper is unit-tested with fakes
- [ ] Shared UI regions (header, nav) are modeled as components kept in a shared component library
- [ ] Generated tests use the helper and the shared components

## Comments

**2026-10-24 — metadata.** The old blocker 08 is wontfix/superseded. The scope needs re-triage against the current pipeline: the shared component library partly exists, the state-setup helper does not.
