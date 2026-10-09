# 06: End-to-end workflow and docs

**What to build:** The CI workflow runs the automation entrypoint on a runner, so that an approved
test-case document ends with one commit on a new branch and an open PR, and a red suite leaves nothing
behind. The change is documented.

**Blocked by:** 01 CI environment skeleton, 05 Automation entrypoint and approval gate.

**Status:** ready-for-agent

- [ ] The workflow invokes the automation entrypoint with the credentials it needs (repo token and model key)
- [ ] An end-to-end dispatch with an approved document is green, then lands one commit on a new branch and an open PR whose body follows the `pr` skill
- [ ] A dispatch where the suite is red creates no branch and no PR
- [ ] README and AGENTS updated (CI now exists; the navigation entrypoint is no longer the only one)
- [ ] Spec and an ADR updated for the decisions (grounding via the browser capability, publishing via git/gh, bot identity)
