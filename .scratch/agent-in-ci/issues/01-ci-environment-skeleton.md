# 01: CI environment skeleton

**What to build:** A manually-triggerable GitHub Actions workflow, living in this repo, that proves a
GitHub-hosted runner can build the environment and run the existing suite green: check out the repo,
sync the Python dependencies, install the Playwright Chromium browser the tests need, then run pytest.
It runs no agent and publishes nothing — it de-risks the runner environment before the agent is wired in.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] A `workflow_dispatch` workflow exists that runs on a GitHub-hosted runner
- [ ] It checks out the repo, installs the Python dependencies, and installs Chromium for Playwright
- [ ] It runs the existing pytest suite on the runner and the run is green
- [ ] It declares the permissions a later publishing step will need (contents and pull-requests write)
- [ ] It installs no Node/`playwright-cli` (grounding moves to the in-process browser capability)
- [ ] Admin note: confirm whether `workflow_dispatch` is enough or a repo secret must be set for the SUT
