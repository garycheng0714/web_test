# 12: Enforce architecture contracts with import-linter

**What to build:** Encode the dependency rules from `AGENTS.md` as import-linter contracts and run
them in CI as a shadow check: shared schemas must not import review or automation, and review must
not import automation.

**Blocked by:** None.

**Status:** ready-for-human (done; required-check decision open)

- [x] Add `import-linter` as a dev dependency
- [x] Define the contracts in `pyproject.toml`
- [x] Add `uv run lint-imports` to `AGENTS.md` and `README.md`
- [x] Add an independent `contracts` job to `.github/workflows/ci.yml`
- [x] Keep the check shadow (visible, not required)
- [x] Record the baseline result
- [x] `uv run pytest` stays green

## Decisions

- Two contracts:
  - **Shared schemas do not import review or automation** — the rule written in `AGENTS.md`.
    Source `web_test.planning.schema`, forbidden `web_test.planning.review` and
    `web_test.automation`.
  - **Review does not import automation** — not written down, added deliberately so the two use
    cases only couple in one direction. It can be relaxed by editing the contract if review ever
    needs automation.
- Independent CI job, so a failure names the check that broke.

## Comments

**2026-10-21 — implemented.**

- `pyproject.toml` holds `[tool.importlinter]` with `root_package = "web_test"` and the two
  forbidden contracts.
- Baseline: `uv run lint-imports` → `Analyzed 39 files, 86 dependencies`, both contracts **KEPT**,
  0 broken.
- CI: `contracts` job runs `uv sync --locked` then `uv run lint-imports`.
- Remaining human decision: whether to make the check required.

**2026-10-24 — bookkeeping: done.**

`ci.yml` runs `uv run lint-imports`; both contracts are kept. The open item is whether to make the job required. Status → `ready-for-human (done; required-check decision open)`.
