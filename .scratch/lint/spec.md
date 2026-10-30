# Lint and format gates

**What to build:** A ruff gate over the code that CI actually runs, rolled out in stages so every
stage lands green.

**Scope:** `web_test/`, `tests/`, `pages/`, `components/`. `main.py` is the navigation demo and stays
out. `pyproject.toml` carries the scope in `[tool.ruff]` `include`, so a bare `uv run ruff check` is
the scoped check.

**Rules as shipped**

| Stage | Rules | Notes |
| --- | --- | --- |
| 0 | `F401`, `I` | established the pipeline: config, CI, pre-commit hook |
| 1 | `UP`, `PIE`, `FURB`, `SIM`, `RET`, `B`, `C4`, `PTH`, `RUF` | `RUF003` ignored (full-width punctuation in prose) |
| 2 | `ARG`, `PLW1510`, `PLR0912`, `PLR2004` | `ARG` and `PLR2004` ignored for `tests/**`; `ARG001` ignored for the two pydantic-ai hook modules whose parameters are called by keyword |
| 3 | `E501`, `E402`, `ISC004` | after `ruff format` at line length 100 |
| 4 | `S` | `S101` and `S105` ignored for `tests/**` |
| post | `PLR0911`, `PLR0913`, `PLR0915` | `max-args = 10`, `max-positional-args = 5`; `max-returns` and `max-statements` keep the ruff defaults |

**Not enabled:** `TRY003`. It requires an exception-class message convention the repo does not have;
its messages are developer diagnostics, not user-facing text.

**Enforcement:** CI runs `uv run ruff check` and `uv run ruff format --check`; the pre-commit hook runs
`ruff check --fix` (failing when it fixes something) and `ruff format`. A `# noqa` must carry a
reason; prefer a documented per-file-ignore over a scattered noqa.

**Invariants:** every stage is green before the next starts; a rule is never satisfied by adding a
bare `noqa`; re-wrapping prose must not change the resulting text.

**Status:** done.
