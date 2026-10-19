# 04: Plan runs in CI from a merged PRD

**What to build:** Merging a PRD PR under `prd/` runs the designer and the advisory Jev review in CI
and opens the test-case PR **as the GitHub App**. The PRD merge is the trigger, and the target
application's base URL comes from the repository variable instead of a local `--base-url` argument.

**Blocked by:** 01 (app identity, secret, and variable), 02 (run-scoped branch names).

**Status:** ready-for-human (done; verified live)

- [x] A new `plan` CI workflow is triggered by a **merged** PR touching `prd/**`, acting on exactly
      one **added** PRD; a change that is not exactly one added PRD fails clearly
- [x] It uses the app token (checkout + `gh`) and read-only workflow permissions, and passes the run
      id/attempt for the branch suffix
- [x] The base URL is read from `WEB_TEST_BASE_URL`; a missing variable fails clearly
- [x] The Jev review appears in the test-case PR body when `TYPESAFE_API_KEY` is present, and is
      omitted (degraded) when it is absent
- [x] The sample PRD is moved under `prd/`, the screenshots move to the repository root, and the
      obsolete manual test-cases artifact is deleted
- [x] A PRD that yields zero cases opens no PR and reports no cases

## Comments

Implemented. `.github/workflows/plan.yml` mirrors `automate.yml`: app token + `contents: read` +
`checkout`/`gh`, finds the single added `prd/*.md` (`git diff --diff-filter=A HEAD^ HEAD`), and runs
`python -m web_test.planning.entrypoint --prd <path> --base-url "${WEB_TEST_BASE_URL:?…}" --workspace .`
with `WEB_TEST_RUN_ID/ATTEMPT` and `TYPESAFE_API_KEY` in the env — so branches are run-scoped and the
Jev review prints when the key is set, degrades silently (omitted from the PR body) when it is not.
No Python changed: `plan()` already returns `NO_CASES` (no PR) and `run_review` already degrades.
Moved `register-login.md` → `prd/register-login.md` (screenshot links repointed to `../screenshots/`),
moved the screenshots to the repo root, deleted the obsolete `test-cases.md`. `uv run pytest`: 103
passed, 1 skipped. `actionlint`: clean apart from a stale-metadata false positive on
`actions/create-github-app-token@v3` (`client-id`), which also fires on the existing `automate.yml`
(the action's real `action.yml` accepts `client-id` and deprecates `app-id`). Live merge verification
is ticket 06.

Verified live. `main` at `9defae0` carries the workflow; merging **PR #8** (which added
`prd/login-smoke.md`) triggered `plan` run **39227687708** (green in 38s, log printed `planned`). It
opened **PR #9** authored by `app/web-test-qa-flow`, branch `plan/login-smoke-39227687708-1`, adding
`test-case/test-case-login-smoke.md` (2 cases, `base_url` from `WEB_TEST_BASE_URL`). PR #9's `ci` run
**executed** and passed `test` in 53s, and its body carried the Jev section
(`Groundedness: 2/2 grounded`) because `TYPESAFE_API_KEY` is set. PR #9 was then **closed unmerged**
(a verification artifact; merging it would have triggered `automate`), and its branch deleted.

## Notes

- Workflow changes only take effect once they land on `main`.
- Only **added** PRDs trigger (not modifications) — matching the existing automation pattern.
- The PRD carries no base URL; the base URL lives in the test-case front-matter, supplied here from
  the repository variable.
