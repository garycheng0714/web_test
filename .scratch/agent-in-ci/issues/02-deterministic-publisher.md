# 02: Deterministic publisher

**What to build:** A publisher that turns the Automation Test artifacts a run produced into a pull
request — without the model carrying file contents. Given the changed files, it re-runs the suite and,
only when it is green, creates one commit, pushes a branch, and opens a PR. Publishing is ordinary code
driving git and the GitHub CLI; it is not a model action.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Collects the changed files and keeps only the paths the write guard already permits (test, page, and component Python files)
- [ ] Re-runs the suite itself; when it is not green it performs no git or gh action
- [ ] On green: sets a git identity, creates a branch named from the feature and date, commits all changed files once with a message derived from the test case ids, pushes, and opens a PR against main
- [ ] All command execution goes through an injected runner, so the behavior is unit-tested (correct args, and the no-op-on-red path) without network
- [ ] The PR body is passed in, not generated here
