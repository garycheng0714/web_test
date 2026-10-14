# 14: Decide how the plan stage supplies base_url

**What to build:** The per-case file needs a `base_url` — the automation `CaseFile` requires it
(`web_test/automation/case_file.py:23`) and `coding_agent.py:62` reads it to ground — but the URL
really lives inside the test steps. Decide and implement the endgame.

**Blocked by:** 12, 13.

**Status:** needs-triage

- [ ] A decision: keep a front-matter `base_url` (and where its value comes from) OR drop it
- [ ] If dropped: `CaseFile.base_url` becomes optional, `coding_agent` infers the URL from the steps, and the samples / `tests/automation/*` / ADR-0006 / spec are updated
- [ ] The generated test's runtime base URL is plumbed from the case (today the suite runs against `DEFAULT_BASE_URL`, `pages/base_page.py:8`)

## Comments

For now the plan stage **keeps** `base_url` in the front-matter, so it stays backward-compatible with
ADR-0006, `CaseFile`, and the existing sample files. The open question is whether that is permanent:
the URL is already present in the steps (e.g. `test-case/test-case-0001.md` step 2), and the automation
side uses the front-matter value only for grounding — the generated test runs against `DEFAULT_BASE_URL`
today (ticket 05 deferred the per-case plumbing).
