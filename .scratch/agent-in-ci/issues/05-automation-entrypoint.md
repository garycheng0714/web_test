# 05: Automation entrypoint and approval gate

**What to build:** A single automation entrypoint that reads the approved test-case document, refuses to
do anything unless the document is approved (the human Gate), hands the whole document to the coding
agent, then hands the resulting changed files and PR body to the publisher. It is the seam the CI
workflow calls.

**Blocked by:** 02 Deterministic publisher, 03 Grounding on the in-process browser capability,
04 Agent-produced PR body.

**Status:** ready-for-agent

- [ ] Refuses to run — no agent call, no publish — when the test-case document is not approved
- [ ] Extracts the test case ids from the approved document for the commit message
- [ ] Wires the coding agent to the publisher, passing the workspace directory through
- [ ] Runnable from the command line and importable for tests
- [ ] Unit-tested with a fake agent and a fake publisher (assembly order, refusal path)
