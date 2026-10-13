# 06: `plan` — PRD to a test-case PR

**What to build:** The `plan` command runs the Test Case designer on the PRD and opens a PR that
adds one `test-case/test-case-<id>.md` per case. Merging that PR is the human Gate (ADR-0006); the
merge then triggers the automation workflow. Not yet implemented.

**Blocked by:** 05

**Status:** ready-for-agent

- [ ] `plan --prd <path>` is a required-argument command; a missing argument prints usage and exits
- [ ] Each case is written to `test-case/test-case-<id>.md` (front-matter: `id`, `base_url`, `requirement_ids`, `priority`, `test_type`) per ADR-0006
- [ ] Ids are `test-case-%04d`, assigned by scanning `test-case/` for the next free number; concurrent PRs are left to git (an add/add conflict) rather than a server-side counter
- [ ] The cases are opened as a single PR for human review (the Gate)
- [ ] Unit-tested with the model overridden; no network

## Comments

Replaces the earlier "write `.scratch/<feature>/test-cases.md` with `approval: draft`" design (which
ADR-0006 supersedes). The designer agent (ticket 05) still produces the structured `QaReport`; this
ticket adds the per-case file writer and the PR, and drops the single-document `render` /
`is_approved` path.
