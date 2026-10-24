# 02: Deterministic publisher

**What to build:** A publisher that turns the Automation Test artifacts a run produced into a pull
request — without the model carrying file contents. Given the changed files, it re-runs the suite and,
only when it is green, creates one commit, pushes a branch, and opens a PR. Publishing is ordinary code
driving git and the GitHub CLI; it is not a model action.

**Blocked by:** None (can start immediately).

**Status:** ready-for-human (done; implemented)

- [x] Collects the changed files and keeps only the paths the write guard already permits (test, page, and component Python files)
- [x] Re-runs the suite itself; when it is not green it performs no git or gh action
- [x] On green: sets a git identity, creates a branch named from the feature and date, commits all changed files once with a message derived from the test case ids, pushes, and opens a PR against main
- [x] All command execution goes through an injected runner, so the behavior is unit-tested (correct args, and the no-op-on-red path) without network
- [x] The PR body is passed in, not generated here

## Comments

Implemented as a package of small modules rather than one file:

- `command.py` — `CommandResult` (with `check()`), `Runner`, `subprocess_runner`.
- `git.py` — `Git` facade (`changed_paths`, `set_identity`, `create_branch`, `add`, `commit`, `push`)
  plus the pure `parse_git_status`; `GitProtocol` is the injected seam.
- `github.py` — `GitHub.open_pull_request` + `GitHubProtocol`.
- `suite.py` — `Suite.is_green` (the publisher re-runs the suite) + `SuiteProtocol`.
- `publish.py` — policy + orchestration: `allowed_paths` (write-guard filter), `branch_name`,
  `commit_message`, and `publish(case_ids, body, git, pr, suite, today)`. It takes the collaborators as
  arguments; the CI entrypoint wires the real ones (ticket 05).

Tests: `test_git.py` (argv per method + failure + `parse_git_status`), `test_github.py` (`gh pr create`
argv + failure), `test_publish.py` (injects `RecordingGit`/`RecordingGitHub`/`StubSuite`; asserts the
call sequence, allowlist filtering, and the no-op-on-red / no-changes paths — no network). Full suite is
green.

**2026-10-24 — bookkeeping: done.**

`web_test/publishing/{git,github,publish}.py` and their tests implement the deterministic publisher. Status → `ready-for-human (done; implemented)`.
