# 13: Lint the workflows with actionlint

**What to build:** Run actionlint over `.github/workflows/` in CI as a shadow check, pinned to a
known actionlint version, with one documented ignore for stale action metadata.

**Blocked by:** None.

**Status:** ready-for-human

- [x] Run actionlint locally and record the baseline
- [x] Pin the actionlint version used in CI
- [x] Add the ignore and its reason
- [x] Add an independent `workflows` job to `.github/workflows/ci.yml`
- [x] Document the local command in `README.md`
- [x] Keep the check shadow (visible, not required)

## Comments

**2026-10-21 — implemented.**

- CI runs `docker run --rm -v "$PWD:/repo:ro" -w /repo rhysd/actionlint:1.7.12`.
- Local: `actionlint` (Homebrew) or the same Docker command.
- Baseline: 4 findings, all one false positive repeated per workflow.
  - `actions/create-github-app-token@v3` is reported as missing required input `app-id` and as
    defining an unknown input `client-id`.
  - The action's own `action.yml` on v3 makes `client-id` the supported input (not required) and
    keeps `app-id` only as a deprecated fallback; actionlint 1.7.12's bundled metadata is stale.
  - The job passes `-ignore 'actions/create-github-app-token'`, with this reason in a workflow
    comment. Remove the ignore when actionlint's metadata or the action changes.
- No other findings: expressions, shell, and runner labels are clean.
- Remaining human decision: whether to make the check required.
