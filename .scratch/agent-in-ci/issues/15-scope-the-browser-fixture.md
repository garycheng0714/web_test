# 15: Scope the browser fixture to the UI tests

**What to build:** Stop non-UI tests from creating a Playwright `BrowserContext`. Today
`tests/conftest.py` has `@pytest.fixture(autouse=True) block_ads(context)`, so every test under
`tests/` requests the session browser and a context, even when it never uses `page`. Scope the ad
blocker to the three browser test modules instead.

This is a pure test refactor: no production code, no test assertion, and no browser-test behavior
changes. The full suite still launches one session browser for the UI tests; the point is to remove
that setup from the planning/automation/unit tests.

**Blocked by:** None (can start immediately).

**Status:** ready-for-human

- [x] `block_ads` is no longer `autouse=True` in `tests/conftest.py`
- [x] `tests/test_home_page.py`, `tests/test_home_header.py`, and `tests/test_test_cases.py` request
      `block_ads` explicitly, for example with a module-level
      `pytestmark = pytest.mark.usefixtures("block_ads")`
- [x] A non-UI test module no longer sets up `context`/`browser`; verify with
      `uv run pytest --setup-plan tests/planning -q` (or an equivalent fixture-plan check)
- [x] `tests/automation/test_coding_agent.py::test_browser_tools_are_dispatched_through_the_agent`
      is unchanged and keeps its own `EgressPolicy`
- [x] The skipped `test_home_header_shows_nav_links` stays skipped
- [x] `uv run pytest` stays at the same result (currently 237 passed, 1 skipped)
- [x] `uv run basedpyright`, `uv run lint-imports`, `uv run ruff check --select F401`, and
      `actionlint` stay green

## Decisions / assumptions

- Keep `block_ads` in `tests/conftest.py`; only the fixture's activation scope changes. Moving the
  UI tests into a subdirectory is unnecessary for this ticket.
- The UI modules are the only callers of the `header` / `home_page` / `test_cases_page` fixtures; they
  can keep using them unchanged.
- The full suite still runs the UI tests and therefore still installs/launches Chromium once. This
  ticket removes the per-test context setup from the non-UI tests, not the browser dependency itself.
- Measure locally with `uv run pytest -q --durations=20` before and after if useful; duration is not
  an acceptance criterion.

## Out of scope

- Moving UI tests into a `tests/ui/` package.
- Marking tests as slow/live or splitting the CI `test` job.
- Changing the advertised browser, the SUT, or the ad-blocking policy.
- Any production code.

**2026-10-23 — implemented.**

- `block_ads` is no longer `autouse` in `tests/conftest.py`.
- `test_home_page.py`, `test_home_header.py`, and `test_test_cases.py` request it with a module-level
  `pytestmark = pytest.mark.usefixtures("block_ads")`.
- `uv run pytest --setup-plan tests/planning -q` shows no `context`, `browser`, `block_ads`, or
  `playwright` setup; the UI module plan still shows `block_ads` and the browser fixtures.
- The skipped header test and the capability-based `test_browser_tools_are_dispatched_through_the_agent`
  are unchanged.
- `uv run pytest`: 237 passed, 1 skipped (10.62s locally); basedpyright, lint-imports, ruff F401, and
  actionlint are green.
