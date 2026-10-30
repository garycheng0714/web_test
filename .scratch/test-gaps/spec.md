# Test gaps and live split

**What to build:** Close the two highest-risk test gaps and stop the default suite from depending on a
third-party site.

**Scope:** `web_test/publishing/github.py`, `web_test/write_guard.py`, and the browser tests under
`tests/test_*.py` that open `automationexercise.com`. No product-code change.

**Shipped**

### `8c0e3f6` Split live browser tests out of the default suite

| File | Change |
| --- | --- |
| `pyproject.toml` | `addopts = ["-m", "not live"]`; the `live` marker registered |
| `tests/test_home_page.py`, `tests/test_home_header.py`, `tests/test_test_cases.py` | `pytestmark = [pytest.mark.live, pytest.mark.usefixtures("block_ads")]` |
| `tests/test_home_header.py` | the known-issue `skip` became `xfail(strict=True)`, so a fixed site fails as XPASS and asks for the marker to be removed |
| `.github/workflows/ci.yml` | new non-blocking `Live browser tests` step (`continue-on-error: true`) after the coverage step |
| `AGENTS.md` | the default test command states it is hermetic; the live command is listed separately |

### `8ba7b15` Cover the remaining GitHub and write-guard branches

| File | Change |
| --- | --- |
| `tests/publishing/test_github.py` | `_describe`'s `RequestFailed` branch (asserts method, URL, status, and the 200-character truncation) and its `RequestTimeout` branch |
| `tests/test_write_guard.py` | `resolve_workspace_path`'s `except OSError` branch |
| `pyproject.toml`, `uv.lock` | `httpx` added to the dev group; the new tests construct `httpx.Request`, `Response`, and `TimeoutException` directly |

**Measurements**

- Default suite: 315 passed, 5 deselected, about 4.4s (13-16s with the live tests included).
- `uv run pytest -m live`: 4 passed, 1 xfailed, about 13s.
- Line coverage: `web_test/publishing/github.py` 97% -> 100%, `web_test/write_guard.py` 96% -> 100%.

**Decisions / assumptions**

- The checked-in `.coverage` was from 22 Oct and reported `github.py` at 27%; a fresh run showed 97%.
  Measure before writing tests; the stale report would have aimed the work at an almost-covered module.
- Live tests stay in the same CI job so `playwright install` is not paid twice; `continue-on-error`
  keeps a third-party outage from blocking a PR.
- pytest accepts a repeated `-m` and the last one wins (verified with `-m usefixtures`), so
  `uv run pytest -m live` overrides the `addopts` exclusion.
- Coverage stays scoped to `web_test`; `pages/` and `components/` are only exercised by the live tests,
  which the default run excludes.
- The branch was first created on top of `feature/designer-evals-claims` and rebased onto
  `origin/main` (`69ab91a`) before any push.

**Next** (not started)

- Coverage gate: `[tool.coverage.run] branch = true`, `source = ["web_test"]`, a measured
  `[tool.coverage.report] fail_under`, and `exclude_lines` for `pragma: no cover` and
  `if __name__ == .__main__.:`.
- pytest hygiene: `--strict-markers`, `--strict-config`, a warning policy measured with `-W error`,
  and a timeout (`pytest-timeout` if it supports pytest 9, otherwise `faulthandler_timeout`).
- Golden tests: `render_report` (FAIL and BLOCKED records) and `render_document` compared against
  files under `tests/fixtures/golden/`, with a documented manual update procedure.

**Status:** shipped
