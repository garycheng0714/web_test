# 03: The automation PR is tested by CI

**What to build:** Merging a test-case PR opens the tests PR **as the GitHub App**, so its
`pull_request` CI actually runs (no "approval required" stall). The PR is authored by the app, the
commit is by the app, and the `test` check registers and executes on the PR.

**Blocked by:** 01 (app identity and secret), 02 (run-scoped branch names).

**Status:** ready-for-agent

- [x] The automation workflow mints an app installation token and uses it for both checkout and `gh`
- [x] Workflow permissions are reduced to read-only (the app token does the writes)
- [x] The run id and attempt are passed to the entrypoint for the branch suffix
- [ ] A real merged test-case triggers a tests PR whose `ci` run **executes jobs** and shows the
      `test` check on the PR (not `action_required`)
- [x] Commit author and PR author are the same app identity

## Comments

Code and workflow done; the live verification (real merged case) is still outstanding. Decided on the
app identity for commits (option B): `BOT_NAME`/`BOT_EMAIL` now `web-test-qa-flow[bot]` /
`344404446+web-test-qa-flow[bot]@users.noreply.github.com` (shared by both stages). `uv run pytest`:
103 passed, 1 skipped.

## Notes

- Today the workflow uses `secrets.GITHUB_TOKEN` for `gh pr create`; the switch is what removes the
  approval-required stall.
- The app token is exposed to the agent's shell; it is short-lived and scoped to this repository.
