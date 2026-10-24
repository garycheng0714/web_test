---
name: page-object-model
description: Use when writing or updating Playwright Python tests in this repo — creating or extending a page object for a screen, modeling a shared UI region as a component, locating elements, or deciding where assertions belong.
---

# Page Object Model

House conventions for Playwright Python tests here. Follow them so generated tests match the
existing suite and a UI change stays a one-place edit.

## Where things live

- `pages/` — one page object per screen, subclassing `BasePage` and defining its `path` property
  (`BasePage.path` is abstract, so a page object without it cannot be instantiated).
- `components/` — shared UI regions reused across pages (e.g. `Header`).
- `tests/` — tests and fixtures; pytest fixtures live in `tests/conftest.py`. Generated tests go
  **directly under `tests/`**, not in a subdirectory.
- No `__init__.py`; imports are top-level (e.g. `from pages.home_page import HomePage`),
  resolved by `pythonpath = ["."]`.

## Rules

1. **Encapsulate locators.** Selectors live inside page objects/components. Tests never contain selectors.
2. **Actions and state queries belong to the page object; test-specific expectations belong to the
   test.** A page object navigates and exposes locators/state queries; assertions about what *this
   test* expects (a specific title, URL, or text) stay in the test — except a page's own readiness
   check (rule 7).
3. **Model shared regions as components.** Header/nav/footer go in `components/` and are composed
   into pages (see `BasePage` composing `Header`).
4. **Reuse and extend before creating.** Read existing `pages/` and `components/` first; extend an
   existing object rather than duplicating it.
5. **Per-feature action catalog.** Add only the actions/queries the current test cases need; do not
   pre-build unused actions.
6. **Prefer role/accessible-name locators**, scoped to the smallest region (e.g.
   `page.get_by_role("banner").get_by_role("link", name=...)`).
7. **Assert with Playwright's auto-retrying `expect(...)`.** In tests, wrap locators/queries in
   `expect(...)`; never use a one-shot `is_visible()` as an assertion. A page object MAY own an
   intrinsic readiness check named `expect_loaded()` that asserts and raises: `BasePage.expect_loaded()`
   checks the URL from `path`, and a subclass overrides it (calling `super()`) to add content unique
   to that page. `expect_loaded()` and page actions return `self`, so same-page calls chain — wrap the
   chain in parentheses to break it across lines (`home_page.open().expect_loaded()`, or one call per
   line with a leading `.` inside `(...)`). Do not chain across page transitions.
8. **Never name a page-object class with a leading `Test`** — pytest collects those. If the domain
   name really starts with it, set the class attribute `__test__ = False`.
9. **Do not change shared constants or helpers** (e.g. `DEFAULT_BASE_URL`) to fit one case; follow
   the repo defaults.
10. **Use the injected fixtures.** Do not call `page.goto` directly or instantiate page objects
    inside tests.
11. **Keep comments minimal**, matching the surrounding code; no banner or explanatory comments.
12. **A readiness check must target content unique to that page** — its URL, title, or an element
    only that page has. Never assert shared chrome (header/nav/footer/logo): it exists on every
    page and would pass without navigation. This constrains page readiness only, not tests whose
    subject *is* the chrome.
13. **A shared component owns the actions on its own elements**, and a page delegates to it — e.g.
    `Header.click_nav_link(name)` plus `HomePage.click_nav_link(name)`. Tests never reach through a
    component (`page.header.nav_link(...).click()`).
14. **A page object defines only its `path` and its actions/queries — it inherits
    `BasePage.__init__(page, header, base_url=...)`.** Do not define `__init__`; if you must, call
    `super().__init__(page, header)`. The shared `Header` comes through the base class.
15. **To upload a file, take `tmp_path` as a test parameter** (not `pytest.tmp_path`), write the
    fixture there — `(tmp_path / "f.txt").write_text("...")` — and call the page object's method that
    runs `set_input_files(str(tmp_path / "f.txt"))`. Never call a `page.context.set_*` method.
16. **The code you write uses Playwright's Python API** (`page.goto`, `page.click`, `expect`,
    `page.on("dialog", lambda d: d.accept())`, ...). The browser **tools** you used to ground
    (`navigate`, `snapshot`, `click`, `handle_next_dialog`, `tabs`) are not Python APIs and must
    never appear in test or page-object code.
17. **Every locator must resolve to exactly one element** — for an action as well as an assertion. A
    bare text/role locator can match a hidden duplicate or a same-named element elsewhere (a page
    "Home" link plus the header's), which fails with a strict-mode violation; scope it to its region
    (`page.locator("#contact-page").get_by_role(...)`) or use a specific class chain
    (`.status.alert.alert-success`), never a page-wide ambiguous locator.
18. **After navigating, wait for the page to settle before interacting** —
    `page.wait_for_load_state("networkidle")`. A URL/title/heading check can pass before the page's
    scripts load, and a form whose submit handler is attached by script then ignores the click: no
    dialog fires and nothing is submitted.
19. **Follow the case's steps in order.** Do not replace a `navigate` or `click` step with a direct
    URL or a page object's `open()`, and do not drop a setup step; a test that skips the case's
    navigation path is not covering that case.
20. **Tag every generated test with its source case.** Decorate each test function with
    `@pytest.mark.case("<file-id>", <case-number>)`: the front-matter `id` and the integer from the
    file's `## Case N:` heading. One marker per test; a case may have more than one test. Add the
    decorator to each test function; do not replace an existing `pytestmark`.

## House example (read these before writing)

- `pages/base_page.py` — `BasePage`: `open(path)` action, abstract `path`, and `expect_loaded()`
  (URL) readiness check; composes `Header`. Subclasses override `expect_loaded()` to add their own
  page-unique content (e.g. `HomePage` checks its title).
- `pages/home_page.py` — `HomePage(BasePage)`: the canonical page object.
- `components/header.py` — `Header`: component with `NAV_NAMES`, `nav_link(name)`,
  `is_visible()`, `is_logo_visible()`.
- `tests/conftest.py` — `header`, `home_page` fixtures (use these to inject page objects).
- `tests/test_home_page.py` — how a test drives a page object and asserts.

## Locator caution

Content that appears only after an interaction (a success message, a confirmation dialog) is not in
the page's initial snapshot; locate it with a unique locator scoped to its region or a specific class
chain (rule 17), not a bare `get_by_text(...)` that can match a hidden duplicate.

Accessible-name matching is substring and case-insensitive by default. When a name must match
exactly, pass `exact=True`. If a snapshot or terminal looks clean but a match fails, inspect
`repr()` for hidden characters (the Products nav link carries a private-use glyph).

## Known SUT traps (automationexercise.com)

- The Contact Us success message renders twice: visible `div.status.alert.alert-success` and hidden
  `div.alert-success.alert` with the same text. Use `.status.alert.alert-success` directly; do not
  spend turns probing the DOM to rediscover it.
- The Products nav link's accessible name is `"\ue8f8 Products"`; match by substring (the `Header`
  component already does).
- Ad interstitials are blocked by the browser policy; do not add ad waits.

## Before you finish

- No selectors in tests. Test-specific assertions stay in tests; a page object owns only its
  `expect_loaded()` readiness check (rule 12).
- Reused or extended existing page objects where possible.
- New files placed in the right directory and importable.
- Every generated test carries `@pytest.mark.case("<file-id>", <n>)` (rule 20).