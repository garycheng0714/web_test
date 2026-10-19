# 04: Plan runs in CI from a merged PRD

**What to build:** Merging a PRD PR under `prd/` runs the designer and the advisory Jev review in CI
and opens the test-case PR **as the GitHub App**. The PRD merge is the trigger, and the target
application's base URL comes from the repository variable instead of a local `--base-url` argument.

**Blocked by:** 01 (app identity, secret, and variable), 02 (run-scoped branch names).

**Status:** ready-for-agent

- [ ] A new `plan` CI workflow is triggered by a **merged** PR touching `prd/**`, acting on exactly
      one **added** PRD; a change that is not exactly one added PRD fails clearly
- [ ] It uses the app token (checkout + `gh`) and read-only workflow permissions, and passes the run
      id/attempt for the branch suffix
- [ ] The base URL is read from `WEB_TEST_BASE_URL`; a missing variable fails clearly
- [ ] The Jev review appears in the test-case PR body when `TYPESAFE_API_KEY` is present, and is
      omitted (degraded) when it is absent
- [ ] The sample PRD is moved under `prd/`, the screenshots move to the repository root, and the
      obsolete manual test-cases artifact is deleted
- [ ] A PRD that yields zero cases opens no PR and reports no cases

## Notes

- Workflow changes only take effect once they land on `main`.
- Only **added** PRDs trigger (not modifications) — matching the existing automation pattern.
- The PRD carries no base URL; the base URL lives in the test-case front-matter, supplied here from
  the repository variable.
