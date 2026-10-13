# 06: End-to-end workflow and docs

**What to build:** The CI workflow runs the automation entrypoint on a runner, so that an approved
test-case document ends with one commit on a new branch and an open PR, and a red suite leaves nothing
behind. The change is documented.

**Blocked by:** 01 CI environment skeleton, 05 Automation entrypoint and approval gate.

**Status:** ready-for-human

- [x] The workflow triggers on a merged `test-case/**` PR and invokes the entrypoint with the credentials it needs (repo token and model key)
- [x] CI runs the suite on every pull request (`.github/workflows/ci.yml`)
- [x] README and AGENTS updated (two entrypoints; CI now exists)
- [x] An ADR records the decisions; the spec rewrite is deferred to the `plan` work
- [ ] An end-to-end merge lands one commit on a new branch and an open PR whose body follows the `pr` skill
- [ ] A merged PR whose suite ends red creates no branch and no PR (the no-op is unit-tested in the publisher; not dispatch-verified)

## Comments

Implemented against the new PR-merge gate (see `docs/adr/0006-pr-merge-gate-and-per-case-artifact.md`):

- `.github/workflows/automate.yml` — now `on: pull_request: types:[closed]` + `paths: ['test-case/**']`,
  gated by `if: github.event.pull_request.merged == true`. It checks out with full history, syncs deps,
  installs Chromium, finds the **single newly added** `test-case/*.md` (`git diff --diff-filter=A`,
  failing when it is not exactly one), then runs
  `python -m web_test.automation.entrypoint --case <file> --workspace .` with `GOOGLE_API_KEY` (secret),
  `WEB_TEST_MODEL` (var, optional) and `GH_TOKEN` (`GITHUB_TOKEN`, same-repo PRs only).
- `.github/workflows/ci.yml` — new; runs `uv run pytest -q` on every pull request, so the coding agent's
  test PR has a status check before a human merges it.
- `README.md`, `AGENTS.md` — document the two entrypoints and the two workflows.
- `CONTEXT.md` — the **Gate** term now means "the `test-case/<id>.md` PR is merged" (was: front-matter
  `approval`).

Not verified: the two end-to-end items need a push and a real merged PR on GitHub; the runner dispatch
has not been executed (same limitation ticket 01 recorded). The red-→-no-PR behavior is covered by
`tests/publishing/test_publish.py` at the unit level.

Deferred: the `plan` agent's PR creation and the `prd-to-tests/spec.md` rewrite (the spec still describes
the old gate/artifact); the front-matter schema in ADR-0006 is the contract they must follow.
