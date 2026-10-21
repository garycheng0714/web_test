# 11: Add a minimal typecheck gate

**What to build:** A local typecheck command and a CI job that catch cross-module type errors in
the Python package without changing runtime behaviour. Start with a bounded scope and a recorded
baseline, then widen only after the gate is green.

**Blocked by:** None (can start immediately).

**Status:** needs-triage

- [ ] Choose the tool (mypy / pyright / basedpyright / ty) and record why
- [ ] Add it as a dev dependency and check in its config
- [ ] Pick the initial scope and third-party import policy
- [ ] Add the `uv run ...` command to AGENTS.md / README
- [ ] Record the baseline: fix errors or list explicit ignores
- [ ] Add the command to `.github/workflows/ci.yml`
- [ ] Decide whether the check is required; if yes, update branch protection
- [ ] `uv run pytest` stays 117 passed, 1 skipped
- [ ] No runtime behaviour changes

## Open decisions

- Tool and strictness.
- Scope: `web_test/planning` first, or all `web_test`.
- Include tests or only production modules.
- Whether missing third-party stubs are ignored globally or per module.
- CI: add a job to `ci.yml` or a separate workflow; if separate, branch protection needs the new
  check.

## Comments

Recent refactors renamed `VerificationStatus`, split the review modules, and changed
`build_record` signatures. Tests cover behaviour but not every cross-module call site.
`AGENTS.md` currently says no typecheck is configured.
