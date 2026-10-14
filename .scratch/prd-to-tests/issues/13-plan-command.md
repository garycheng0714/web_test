# 13: `plan` command — assign ids and open the test-case PR

**What to build:** A `plan` entrypoint that runs the Test Case designer on a PRD, assigns
`test-case-%04d` ids by scanning `test-case/`, writes one file per case (ticket 12's `render_case`),
and opens one PR adding them — the human Gate.

**Blocked by:** 12.

**Status:** needs-triage

- [ ] `plan --prd <path>` is a required-argument command; a missing argument prints usage and exits
- [ ] Each case is written to `test-case/test-case-<id>.md`, ids assigned by scanning `test-case/` for the next free `%04d`
- [ ] The cases are opened as a single PR against `main` (the Gate)
- [ ] Runnable from the command line and importable, like `web_test/automation/entrypoint.py`
- [ ] Unit-tested with the model overridden and fake `git`/`gh` (no network)

## Comments

This supersedes `06-plan-cli.md` (same scope, rewritten for the ticket-12 format). Its id policy stands:
`test-case-%04d`, assigned by scanning `test-case/` rather than a server-side counter, so concurrent
PRs are left to git (an add/add conflict).

Open (discuss before implementing):

- **Branch name** — relates to agent-in-ci ticket 10 (collision). Where the PR branch comes from.
- **Commit and PR messages**, and the PR body's shape.
- **Re-run/duplication** — a second `plan` run assigns new ids and adds duplicate cases; decide the policy.
- **Reuse** `web_test/publishing/` `Git`/`GitHub`, or a small dedicated publisher (the current
  `Publisher.publish` is single-case and hardcodes `automation/<id>`).
- **Local vs CI** — the spec (`prd-to-tests/spec.md:94`) says `plan` may run locally; it needs push + `gh`.
