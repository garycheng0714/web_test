# 09: Re-run the agent from PR review comments

**What to build:** After a human reviews the generated tests PR (`automation/**`) and leaves
comments, the agent can be re-triggered to apply the requested changes on the same PR.

**Blocked by:** None (06 and 10 complete).

**Status:** needs-triage

- [ ] A comment on an `automation/**` PR re-triggers the agent, for authorized users only
- [ ] The agent works on the PR's **head branch** and adds a commit (the PR updates in place)
- [ ] A red update leaves the branch unchanged and reports the failure on the PR
- [ ] No trigger loop (bot/self comments ignored); concurrent updates are serialized
- [ ] A new ADR / spec revision replaces the "PR review gate after automation is out of scope" line

## Comments

The only trigger today is "a merged `test-case/**` PR" (`.github/workflows/automate.yml`).
`.scratch/prd-to-tests/spec.md:201` explicitly lists "A PR review gate after automation; only the
test-case review gate exists in v1" as Out of Scope, so this feature needs an ADR and a spec change
first.

Sketch (implementation details to decide later):

- **Trigger:** `on: issue_comment: types:[created]`, filtered to pull requests whose head is
  `automation/**` and to a slash command (e.g. `/agent <feedback>`).
- **Authorization:** only `author_association` in {OWNER, MEMBER, COLLABORATOR} (a public repo must
  not let anyone spend the model key).
- **Input:** check out the PR head branch (not `main`), read `test-case/<id>.md`, pass the comment
  text as feedback to the coding agent.
- **Output:** one new commit on the same branch. Needs new publisher surface: `Git.fetch` /
  `Git.checkout` (today only `create_branch`, `web_test/publishing/git.py:35`) and
  `GitHub.edit_pull_request` / `GitHub.comment` (today only `open_pull_request`,
  `web_test/publishing/github.py:22`).
- **Red:** leave the branch untouched and post a failure comment (needs `issues: write`).

Open: slash command vs any comment; who may trigger; red behavior (comment vs silent); whether to
also update the PR body.

**2026-10-24 — metadata.** 06 and 10 are done (run-scoped branch names), so this is unblocked. The trigger, permission, and red-behavior decisions are still open.
