# 11: Add a minimal typecheck gate

**What to build:** A local typecheck command and a CI job that catch cross-module type errors in
the Python package without changing runtime behaviour. Start with a bounded scope and a recorded
baseline, then widen only after the gate is green.

**Blocked by:** None (can start immediately).

**Status:** ready-for-human (done; required check)

- [x] Choose the tool (mypy / pyright / basedpyright / ty) and record why
- [x] Add it as a dev dependency and check in its config
- [x] Pick the initial scope and third-party import policy
- [x] Add the `uv run ...` command to AGENTS.md / README
- [x] Record the baseline: fix errors or list explicit ignores
- [x] Add the command to `.github/workflows/ci.yml`
- [x] Decide whether the check is required; if yes, update branch protection
- [x] `uv run pytest` stays green (138 passed, 1 skipped)
- [x] No runtime behaviour changes

## Decisions

- Tool: `basedpyright` 1.40.2. It installs from PyPI through `uv` and brings its own Node wheel
  (`nodejs-wheel-binaries`), so no separate Node setup is needed. It understands Pydantic without a
  plugin. `mypy` would need the Pydantic plugin and `types-PyYAML`; `ty` is still 0.0.x.
- Strictness: `typeCheckingMode = "standard"`.
- Scope: `web_test` only. All 118 functions there are annotated; `tests` has 109 unannotated
  functions and would add noise before a wider pass.
- Third-party policy: no stubs were needed. `pyyaml` has no `py.typed`, and standard mode accepts the
  resulting untyped `yaml.safe_load`; no global `ignore_missing_imports` was added.
- CI: a `typecheck` job in `.github/workflows/ci.yml`, required on `main` since 2026-10-24.

## Comments

Recent refactors renamed `VerificationStatus`, split the review modules, and changed
`build_record` signatures. Tests cover behaviour but not every cross-module call site.
`AGENTS.md` currently says no typecheck is configured.

**2026-10-21 — implemented.**

- Config: `[tool.basedpyright]` in `pyproject.toml` (`include = ["web_test"]`,
  `typeCheckingMode = "standard"`).
- Baseline: 2 errors, both fixed without behaviour changes.
  - `web_test/model.py`: the DeepSeek profile passed OpenAI-only keys to `ModelProfile`; it now
    builds `OpenAIModelProfile` (the TypedDict that declares them).
  - `web_test/write_guard.py`: narrowed `str | None` to `str` before `ModelRetry`; same guard as
    `permission.allow`.
- Result: `uv run basedpyright` → **0 errors, 0 warnings, 0 notes**.
- `uv run pytest -q` → 138 passed, 1 skipped.
- Commands documented in `AGENTS.md` and `README.md`.
- Remaining human decision: whether to make the check required (branch protection).

**2026-10-24 — bookkeeping: done.**

`ci.yml` runs `basedpyright` and `ruff check --select F401`. The only open item is whether to make the job required; that box is left unchecked. Status → `ready-for-human (done; required-check decision open)`.

**2026-10-24 — required.** `typecheck` is a required status check on `main` (app id 15368), together with `test`, `contracts`, and `verify-test-case`; `workflows` stays shadow. Status → `ready-for-human (done; required check)`.
