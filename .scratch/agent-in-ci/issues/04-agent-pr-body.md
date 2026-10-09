# 04: Agent-produced PR body

**What to build:** After the generated tests pass, the same coding agent writes the PR body following the
repo's `pr` skill (Summary / Evidence / Merge Danger), and the automation stage returns that body for the
publisher to use. A red suite produces no body.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] The coding agent can load the `pr` skill on demand
- [ ] On green, the agent's output is a PR body following the skill's template
- [ ] On red, the agent stops and produces no PR body
- [ ] An agent-level test (model overridden) asserts red produces no body and green produces one
