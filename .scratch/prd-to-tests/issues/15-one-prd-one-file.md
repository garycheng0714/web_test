# 15: One PRD, one test-case file (artifact shape)

**What to build:** Change the plan stage's artifact from **one file per case**
(`test-case/test-case-<id>.md`) to **one file per PRD** (`test-case/<prd-stem>.md`), holding that
PRD's cases as sections. Supersedes ADR-0006's artifact section (a new ADR follows once the open
items below are decided).

**Blocked by:** None to decide; implementation reworks 12 and 13.

**Category:** enhancement

**Status:** needs-triage

- [ ] One file per PRD: `test-case/<prd-stem>.md` (e.g. `test-case/register-login.md`)
- [ ] Front-matter: `id` (＝ the PRD stem) and `base_url`
- [ ] Body: a PRD-level title/summary, then one section per case; each case carries a small
      machine-readable YAML block (`requirement_ids`, `priority`, `test_type`) plus the
      human-readable requirements/preconditions/steps/notes
- [ ] Re-planning the same PRD **overwrites** `test-case/<prd-stem>.md`
- [ ] The rendered file still parses (front-matter `id`/`base_url`) for the automation entrypoint
- [ ] A new ADR supersedes ADR-0006's "one case per file" artifact section; the spec is updated

## Comments

Decisions from review:

- **One PRD per file.** The current PRDs happen to be single-module, so "one module per file" and
  "one PRD per file" coincide; "one PRD per file" avoids inventing a module vocabulary (`module_feature`
  is free text today, and requirement ids only imply a module via the `FR-<MODULE>-` prefix).
- **Filename `test-case/<prd-stem>.md`**; front-matter `id` == the PRD stem.
- **Front-matter shape C (hybrid):** minimal top front-matter (`id`, `base_url`) + a per-case
  machine-readable YAML block in the body, so the file stays human-reviewable (the Gate) yet tooling
  can read per-case `requirement_ids`/`priority`/`test_type`.
- **Same-name re-plan overwrites.**

Artifact sketch:

````markdown
---
id: register-login
base_url: https://automationexercise.com
---

# Register / Login / Logout

## Case 1: 會員 / 註冊 Step 1（Name + Email）

```yaml
requirement_ids: [FR-ACC-01]
priority: High
test_type: Functional
```

**Preconditions**
- ...

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | ... | ... |

## Case 2: ...
````

Open (decide later):

- **Automation unit** — one run implements the whole file, or one run per selected case within the
  file (`--case <file> --select <case-id>`).
- **Red policy** — with multiple cases per file, does one red case block the whole file (no PR), or
  do green tests ship with a visible fixme for the red case (the spec already allows a fixme for
  non-automatable cases)?
- **Overwrite vs merge-trigger detection** — `automate.yml` finds the en‑tirely new file with
  `git diff --diff-filter=A` and ADR-0006 states "editing an existing file does not trigger". A
  same-name re-plan makes the file **modified (M)**, not added (A), so it would not trigger (and the
  "exactly one added file" check fails). Needs a resolution: trigger on add **or** modify, emit a new
  numbered file for a re-plan, or accept that an overwrite does not auto-trigger.

Impact (implementation, once the open items are decided):

- `web_test/planning/cases_writer.py` — `render_case` → a `render_document(cases, *, id, base_url)`;
  `CaseWriter` writes one `<prd-stem>.md`; `assign_ids` retires (stem-based naming).
- `web_test/planning/entrypoint.py` — file name = `<prd.stem>.md`; overwrite an existing file.
- `web_test/planning/publisher.py` — `PlanPublisher.publish` takes the single file; branch/message
  from the PRD stem.
- `web_test/automation/case_file.py` — `from_path` path validation accepts `test-case/<any>.md`
  (today it requires `test-case-*.md`); `CaseFile` still reads only the front-matter.
- `web_test/automation/coding_agent.py` — `create_automation` receives the whole file (multi-case).
- `.github/workflows/automate.yml` — the added-file detection (see the conflict above).
- Ticket 08 (per-test case-id tags) reads the per-case YAML block.
- `docs/adr/` (new ADR), `.scratch/prd-to-tests/spec.md`.
