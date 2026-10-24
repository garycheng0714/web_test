# 20: Name the phases in the automation entrypoint

**What to build:** `automate()` was the change hotspot (226 lines: agent, quality gate, suite,
report, publish, evidence). Extract two named phases with explicit contracts, keeping the outcome
branching and exception handling in `automate()`. Pure refactor: no behavior change, no new module,
no state object.

**Shape:**

- `_run_suite(suite: Suite, workspace: Path, files: Sequence[str])
  -> tuple[CommandResult, RunReport]` (runs the suite, reads JUnit, builds the report)
- `_publish(case_id: str, pr_body: str, report: RunReport, files: list[str], *, git: Git,
  pr: GitHubAdapter, token: str | None) -> None` (appends the report and publishes)
- `quality_findings` stays inline: wrapping it in a one-line `_quality_gate` alias adds
  indirection without a phase of its own.
- Invariant: `automate()` still owns the `AGENT_RED` / `QUALITY_RED` / `SUITE_RED` /
  `NO_CHANGES` / `PUBLISHED` / `FAILED` branching.

**Blocked by:** None (10b done; merged in #35).

**Status:** ready-for-human (done; implemented)

**Priority:** low — it was 226 lines; the value was change locality, not behavior.

- [x] The two phases have the contracts above and no other logic
- [x] `automate()` keeps the outcome branching and the exception handling
- [x] No new module, no state object, no behavior change
- [x] `tests/automation/test_entrypoint.py` passes unchanged
- [x] `uv run pytest`, `uv run basedpyright`, `uv run ruff check --select F401`,
      `uv run lint-imports`, and `actionlint` pass

## Out of scope

- Changing the gate, the report format, or the quality rules.
- Adding a `Run`/`Pipeline` object or splitting `automate()` into one function per branch.
- Moving the entrypoint to a new module.

**2026-10-25 — implemented.**

- `web_test/automation/entrypoint.py`: `automate()` is now ~78 lines; the suite/JUnit/report work is
  `_run_suite`, and the body composition + publish is `_publish`.
- `quality_findings` stays inline; a one-line `_quality_gate` alias would add indirection without a
  phase of its own.
- The outcome order (`AGENT_RED` → `QUALITY_RED` → `SUITE_RED` → `NO_CHANGES` → `PUBLISHED` /
  `FAILED`) and the exception handling are unchanged.
- `tests/automation/test_entrypoint.py` passes unchanged; no new module or state object.
- `uv run pytest`: 304 passed, 1 skipped; basedpyright, ruff F401, lint-imports, and actionlint are
  green.
