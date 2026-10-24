# 01: Provision the GitHub App identity and repository settings

**What to build:** A GitHub App `web-test-QA-flow` exists and is installed on this repository with
Contents and Pull-requests write; its Client ID and private key are repository secrets; the base URL
and merge settings are configured. This is the identity and settings prerequisite both CI stages need
(today the PRs are opened with `GITHUB_TOKEN`, whose pull_request runs stall as "approval required").

**Blocked by:** None (can start immediately).

**Status:** ready-for-human (done; verified live)

- [x] App `web-test-qa-flow` created: webhook off; Contents read/write; Pull-requests read/write;
      installed **only** on this repository
- [x] Repository secrets set: `APP_CLIENT_ID`, `APP_PRIVATE_KEY` (the private key never committed)
- [x] Repository variable `WEB_TEST_BASE_URL` = `https://automationexercise.com`
- [x] "Automatically delete head branches" enabled
- [x] Branch protection on `main`: require the `test` status check; **no** required review; direct
      pushes still allowed; admins may bypass

## Comments

Verified via API: secrets `APP_CLIENT_ID` / `APP_PRIVATE_KEY` present; variable `WEB_TEST_BASE_URL` =
`https://automationexercise.com`; `delete_branch_on_merge = true`; branch protection on `main`
requires the `test` check (`strict: false`, no required reviews, `enforce_admins: false`). The app was
renamed to `web-test-qa-flow`; its bot user is `web-test-qa-flow[bot]` (id 344404446).

## Notes

- Short-lived installation tokens (≈1 hour) outlast the 30-minute jobs, so no re-mint is needed.
- The app authors the PRs, so a human (not the app) can approve them if a review gate is ever added.

**2026-10-24 — bookkeeping: done.**

The `web-test-qa-flow` app, its secrets, and the repository variable are in use by both workflows. Status → `ready-for-human (done; verified live)`.
