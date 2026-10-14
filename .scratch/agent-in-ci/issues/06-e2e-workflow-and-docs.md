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
- [x] An end-to-end merge lands one commit on a new branch and an open PR whose body follows the `pr` skill
- [x] A merged PR whose suite ends red creates no branch and no PR (the no-op is unit-tested in the publisher; not dispatch-verified)

## Comments

Implemented against the new PR-merge gate (see `docs/adr/0006-pr-merge-gate-and-per-case-artifact.md`):

- `.github/workflows/automate.yml` — now `on: pull_request: types:[closed]` + `paths: ['test-case/**']`,
  gated by `if: github.event.pull_request.merged == true`. It checks out with full history, syncs deps,
  installs Chromium, finds the **single newly added** `test-case/*.md` via
  `git diff --name-only --diff-filter=A HEAD^ HEAD -- 'test-case/*.md'` (covers merge/squash merges;
  fails when it is not exactly one), then runs
  `python -m web_test.automation.entrypoint --case <file> --workspace .` with `OPENCODE_API_KEY`
  (secret), `GH_TOKEN` (`GITHUB_TOKEN`, same-repo PRs only), and — since the run needs a capable model
  and enough repair budget — `WEB_TEST_MODEL` (`vars.WEB_TEST_MODEL || 'openai-chat:kimi-k2.7-code'`) and
  `WEB_TEST_REPAIR_ATTEMPTS` (`vars.WEB_TEST_REPAIR_ATTEMPTS || '10'`), both overridable via repo
  variables.
- `.github/workflows/ci.yml` — new; runs `uv run pytest -q` on every pull request, so the coding agent's
  test PR has a status check before a human merges it.
- `README.md`, `AGENTS.md` — document the two entrypoints and the two workflows.
- `CONTEXT.md` — the **Gate** term now means "the `test-case/<id>.md` PR is merged" (was: front-matter
  `approval`).

Not verified: the red-→-no-PR behavior is covered by `tests/publishing/test_publish.py` at the unit level
only; it was not dispatch-verified (a dispatch red would need a case whose generated suite stays red).

Dispatch-verified (item 1): another merged `test-case/**` PR, `test-case/test-case-0003.md`
(squash-merged as `af01225`), triggered `automate` run
[`38530673108`](https://github.com/garycheng0714/web_test/actions/runs/38530673108) — green in 12m57s.
It pushed exactly one commit (`300521e`, "Add automated tests for test-case-0003") on the new branch
`automation/test-case-0003` and opened PR
[#4](https://github.com/garycheng0714/web_test/pull/4) (base `main`) whose body follows the `pr`
skill (Summary / Evidence / Merge Danger). Notes for a rerun:

- The repo needs **Settings → Actions → General → Allow GitHub Actions to create and approve pull
  requests** (`can_approve_pull_request_reviews: true`). Without it, the run reaches the publisher,
  pushes the branch, then fails at `gh pr create` with "GitHub Actions is not permitted to create or
  approve pull requests" (this happened on the first attempt, run `38527852533`; the branch
  `automation/test-case-0002` was left orphaned, and its `pr_body` was lost).
- `default_workflow_permissions` is `read`, which is fine: `automate.yml` declares
  `permissions: contents: write, pull-requests: write`, and the branch push already succeeded under it.
- Re-running needs a **new** `test-case/<id>.md`; editing an existing one adds no file and fails the
  `--diff-filter=A` "exactly one added" check.

Deferred: the `plan` agent's PR creation and the `prd-to-tests/spec.md` rewrite (the spec still describes
the old gate/artifact); the front-matter schema in ADR-0006 is the contract they must follow.
