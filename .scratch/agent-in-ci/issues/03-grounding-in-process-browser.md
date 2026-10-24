# 03: Grounding on the in-process browser capability

**What to build:** Move the coding agent's live grounding off the external `playwright-cli` and onto the
Pydantic AI Harness browser capability (in-process Python Playwright). The agent reads a page as an
accessibility tree with `aria-ref` handles and targets elements by those handles, exactly as it did with
the CLI snapshot — but without Node, npm, or a global CLI in the environment.

**Blocked by:** None (can start immediately).

**Status:** ready-for-human (done; implemented)

- [x] The coding agent exposes the browser capability's navigate and accessibility-snapshot tools
- [x] Grounding instructions name the capability's tools instead of the external CLI
- [x] The page-object skill's grounding wording still holds (snapshot-based, `aria-ref` targeting)
- [x] No Node/npm/`playwright-cli` step is required for the agent to ground
- [x] Verified at the unit level that the capability and its snapshot tool are attached
- [x] Verified by a local smoke run that it can ground a real page

## Comments

Implemented:

- `web_test/automation/coding_agent.py` — added `PlaywrightBrowser(policy=GROUNDING_POLICY)`
  to the agent's capabilities. `GROUNDING_POLICY` is an `EgressPolicy` that allows the SUT
  (`automationexercise.com`) and blocks the ad networks seen injecting the interstitial
  (`AD_DOMAINS`, the same list as `tests/conftest.py`'s `block_ads`). The `allowed_domains`
  shorthand cannot do this: it leaves passive subresources and sub-frames unbounded, which is
  exactly where the ad script/frame live; `blocked_domains` reaches every request kind. The browser
  launches on first use and closes with the run. Rewrote the grounding paragraph of `INSTRUCTIONS`
  to name `navigate(<url>)` / `snapshot()` and target by the `aria-ref` handles the snapshot
  returns — no `playwright-cli`, no open/close step. Extracted
  `build_automation_agent(model, *, workspace_dir) -> Agent` out of `create_automation` so the
  assembled agent (capabilities + tools) is inspectable without a run.
- `pyproject.toml` — harness dependency is now `pydantic-ai-harness[coder,playwright,skills]`; `uv lock`
  refreshed (the `playwright`/`idna` requirement was previously only satisfied transitively by the dev
  group).
- `tests/automation/test_coding_agent.py` — four tests. Three are pure (`TestModel`; no browser,
  no network): the capability/toolset + policy-wiring check; an `EgressPolicy.refuse` check that ad
  subresources/sub-frames are blocked while the SUT navigation is allowed; and an instruction-wording
  guard. The fourth scripts the model (`FunctionModel` + a stream function, since `Coder` streams) to
  actually call `navigate` and `snapshot` **through the agent**, then asserts the tool returns came
  back from the dispatched tools and the snapshot carried `ref=e` handles — real Chromium, real page.
- Page-object skill: `page-object-model/SKILL.md` has no grounding wording (only its snapshot-aware
  Locator caution), so nothing to change — the snapshot/`aria-ref` concept carries over unchanged.

Smoke run: the through-the-agent test above grounds the configured SUT
(`https://automationexercise.com`) with in-process Chromium and asserts `navigate`/`snapshot`
dispatch. A separate ad-hoc run drove `PlaywrightBrowserSession` directly against the same URL →
title `Automation Exercise`, 721 `aria-ref` handles. Note: `example.com` does not resolve in this
environment (the capability's private-address block refuses an unresolved host), so the SUT was used.

`uv run pytest`: 50 passed, 1 skipped (the pre-existing Products PUA header test).

Left for ticket 06: `AGENTS.md` and `README.md` still describe grounding via `playwright-cli`.

**2026-10-24 — bookkeeping: done.**

`web_test/automation/coding_agent.py` grounds through the in-process `PlaywrightBrowser` capability. Status → `ready-for-human (done; implemented)`.
