# 03: Grounding on the in-process browser capability

**What to build:** Move the coding agent's live grounding off the external `playwright-cli` and onto the
Pydantic AI Harness browser capability (in-process Python Playwright). The agent reads a page as an
accessibility tree with `aria-ref` handles and targets elements by those handles, exactly as it did with
the CLI snapshot — but without Node, npm, or a global CLI in the environment.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] The coding agent exposes the browser capability's navigate and accessibility-snapshot tools
- [ ] Grounding instructions name the capability's tools instead of the external CLI
- [ ] The page-object skill's grounding wording still holds (snapshot-based, `aria-ref` targeting)
- [ ] No Node/npm/`playwright-cli` step is required for the agent to ground
- [ ] Verified at the unit level that the capability and its snapshot tool are attached
- [ ] Verified by a local smoke run that it can ground a real page
