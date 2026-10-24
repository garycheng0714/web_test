# 20: Name the phases in the automation entrypoint

**What to build:** `automate()` is the change hotspot (226 lines: agent, quality gate, suite,
report, publish, evidence). Extract three named phases with explicit contracts, keeping the outcome
branching and exception handling in `automate()`. Pure refactor: no behavior change, no new module,
no state object.

**Shape:**

- `_quality_gate(case_id: str, text: str, files: Sequence[str], workspace: Path)
  -> tuple[QualityFinding, ...]`
- `_run_suite(suite: Suite, workspace: Path, files: Sequence[str])
  -> tuple[CommandResult, RunReport]` (runs the suite, reads JUnit, builds the report)
- `_publish(case_id: str, pr_body: str, report: RunReport, files: list[str], git: Git,
  pr: GitHubAdapter, token: str | None) -> None` (appends the report and publishes)
- Invariant: `automate()` still owns the `AGENT_RED` / `QUALITY_RED` / `SUITE_RED` /
  `NO_CHANGES` / `PUBLISHED` / `FAILED` branching.

**Blocked by:** 10b (run report; the same function is changing there).

**Status:** ready-for-agent

**Priority:** low — 226 lines today; do it before the next automation feature, not before 10b.

- [ ] The three phases have the contracts above and no other logic
- [ ] `automate()` keeps the outcome branching and the exception handling
- [ ] No new module, no state object, no behavior change
- [ ] `tests/automation/test_entrypoint.py` passes unchanged
- [ ] `uv run pytest`, `uv run basedpyright`, `uv run ruff check --select F401`,
      `uv run lint-imports`, and `actionlint` pass

## Out of scope

- Changing the gate, the report format, or the quality rules.
- Adding a `Run`/`Pipeline` object or splitting `automate()` into one function per branch.
- Moving the entrypoint to a new module.
