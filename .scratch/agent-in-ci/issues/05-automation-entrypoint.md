# 05: Automation entrypoint and approval gate

**What to build:** A single automation entrypoint that reads one merged `test-case/<id>.md`, has the
coding agent implement it, and hands the resulting PR body to the publisher. It is the seam the CI
workflow calls. (The approval gate is the PR merge, handled by the trigger in ticket 06 — not a
runtime check.)

**Blocked by:** 02 Deterministic publisher, 03 Grounding on the in-process browser capability,
04 Agent-produced PR body.

**Status:** ready-for-human

- [x] An entrypoint reads one merged `test-case/<id>.md` and has the coding agent implement it
- [x] Validates the artifact (path shape + front-matter `id`/`base_url`); rejects anything else
- [x] Wires the coding agent to the publisher, passing the workspace through; branch/commit come from the case id
- [x] Runnable from the command line and importable for tests
- [x] Unit-tested with a fake agent and fake `git`/`pr`/`suite` (ordering, red skips publish, path validation)

## Comments

**Design superseded.** The old gate — "refuses unless the test-case document is approved" via a
front-matter `approval` state — is replaced by the PR-merge gate: the workflow only runs after a
`test-case/<id>.md` PR is merged, so approval is the merge, handled by the trigger (ticket 06), not a
runtime check. There is no `is_approved` in the entrypoint; the whole qa-table document is gone in
favour of one front-matter file per case.

Implemented:

- `web_test/automation/entrypoint.py` — `CaseFile(BaseModel)` (`id`, `base_url`, optional
  `requirement_ids`/`priority`/`test_type`, YAML front-matter) + `parse_case`; `_validate_case_path`
  (must be `test-case/test-case-*.md`); `automate(case_path, *, workspace, agent=create_automation,
  publisher)` — read case → hand the raw document to the agent → publish only when the agent's
  `pr_body` is present; and `main()` (`--case`, `--workspace`) binding `publish` to real
  `Git`/`GitHub`/`Suite`.
- `web_test/publishing/publish.py` — `publish` now takes `case_id` (not `case_ids` + `FEATURE`);
  `branch_name(id) = automation/<id>`, `commit_message(id) = Add automated tests for <id>`.
- `web_test/paths.py` — dropped the unused `FEATURE` constant (publish no longer needs it).
- `web_test/automation/coding_agent.py` — `INSTRUCTIONS` take the base URL from the case's
  front-matter `base_url` (was: case text or `DEFAULT_BASE_URL`).
- `pyproject.toml` — `pyyaml` promoted to a direct dependency (front-matter has a YAML list).
- `test-case/test-case-0001.md` — a hand-written sample so the entrypoint can be built and tested
  without the `plan`→PR path (deferred).
- Tests: `tests/automation/test_entrypoint.py` (front-matter parsing/defaults/validation; ordering;
  red skips publish) and updated `tests/publishing/test_publish.py` for the `case_id` interface.

`uv run pytest`: 58 passed, 1 skipped (the pre-existing Products PUA header test).

Deferred: the `plan` agent producing these per-case files + PR (front-matter schema to be shared),
and the per-case `base_url` → generated-test runtime plumbing (`DEFAULT_BASE_URL` is used for now).
