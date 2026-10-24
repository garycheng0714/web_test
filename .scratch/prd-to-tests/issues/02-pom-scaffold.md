# 02: Page Object Model scaffold

**What to build:** The Page Object Model scaffold the automator will generate into: a base
page, one canonical example page object, and a fixture that injects page objects. A developer
can run a smoke test that drives the app through a page object.

**Blocked by:** 01

**Status:** ready-for-human (done; implemented)

- [x] A base page and one canonical example page object are checked in as the house pattern
- [x] Locators are encapsulated in page objects; assertions live in the tests (the example demonstrates both)
- [x] Page objects expose actions and state queries
- [x] A fixture injects page objects into tests
- [x] A smoke test uses the page object via the fixture and passes

## Comments

Implemented the POM scaffold:

- `pages/base_page.py` — `BasePage`: holds `page`, `base_url` (default
  `https://automationexercise.com`), and a composed cross-page `Header` component; exposes the
  `open(path)` action and `title()`/`url()` state queries.
- `pages/home_page.py` — `HomePage(BasePage)`: the canonical example; exposes the nav-link
  locators by delegating to the composed `Header` component (`nav_link(name)`), and inherits the
  `open()` action.
- `components/header.py` — added `NAV_NAMES` and `nav_link(name)`, locating nav links by
  accessible name (`get_by_role("link", name=...)`, substring match) scoped to the header list;
  the PUA glyph on the Products link is tolerated by the substring match and stays visible in
  `nav_names()` / the Header test.
- `tests/conftest.py` — added a `home_page` fixture (kept the existing `header` fixture).
- `tests/test_home_page.py` — two smoke tests drive the app through the page object via the
  fixture (page load + all nav links resolve); assertions live in the tests, selectors do not.

No `__init__.py` files, matching `components/` (relies on `pythonpath = ["."]`).

Known pre-existing failure left untouched per maintainer decision:
`tests/test_home_header.py::test_home_header_shows_nav_links` — `Header.nav_names()` returns the
real accessible name `"\ue8f8 Products"` for the Products link (see `.scratch/known-issues.md`).
The ticket 02 smoke test itself passes; `uv run pytest` is otherwise green.

**2026-10-24 — bookkeeping: done.**

`pages/` and `components/` provide the Page Object Model scaffold. Status → `ready-for-human (done; implemented)`.
