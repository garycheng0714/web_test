# 07: Evidence for red runs

**What to build:** When an automation run ends without publishing (`AGENT_RED`, `SUITE_RED`, `FAILED`,
or `NO_CHANGES`), keep enough evidence to diagnose it and make the red outcome visible. Today the
runner is ephemeral and the decisive pytest output is discarded, so a red run leaves only a job that
looks green and a log with no failure detail. This ticket adds the missing evidence; it does **not**
change the gate (ADR-0006 still holds: red opens no branch and no PR).

**Blocked by:** 05 Automation entrypoint and approval gate, 06 End-to-end workflow and docs.

**Status:** ready-for-agent

- [ ] The pytest output of the run that **decided** red is kept (not just a fresh re-run, which can
      pass on the flaky SUT and hide the failure)
- [ ] The agent's generated files are captured, including **untracked** new files (`git diff` alone misses them)
- [ ] The agent's tool-call sequence is logged even when the repair budget is exhausted
- [ ] The outcome and the evidence are surfaced: a job summary line and an uploaded workflow artifact
- [ ] `WEB_TEST_USAGE` (and `WEB_TEST_TRACE`) are on for the automate run
- [ ] The artifact excludes `.playwright-cli/` and `.venv` (the CLI state may hold credentials — see AGENTS.md)
- [ ] Unit-tested: the component that runs the suite keeps the failing output for the caller

## Comments

Why the earlier "just re-run `uv run pytest` and upload it" sketch is not enough, with the code spots:

- `web_test/publishing/suite.py:13` — `Suite.is_green` keeps only `returncode`; the stdout/stderr of
  the run that returned red is **discarded**. A second run may pass (the Contact Us SUT flakes — see
  `model-runs.md`), erasing the failure. Keep the deciding run's output.
- `web_test/publishing/git.py:29` — `changed_paths` uses `git status --porcelain`, which **does** see
  untracked files, but `git diff` does not. The agent writes new files, so capture `tests/`, `pages/`,
  `components/` (archive them) or stage-then-diff, not a bare `git diff`.
- `web_test/automation/coding_agent.py:132-134` — on `RepairBudgetExceeded`, `create_automation`
  returns `AutomationResult(pr_body=None)` **without** calling `log_trace`, so a budget-exhausted run
  prints no trace even with `WEB_TEST_TRACE=1`.
- `web_test/observability.py:53` — `_clip` truncates tool output to 160 chars; fine for tool args, not
  for pytest output.
- `.github/workflows/automate.yml` — sets neither `WEB_TEST_USAGE` nor `WEB_TEST_TRACE`, and publishes
  no artifact; `main()` returns 0 on `AGENT_RED`/`SUITE_RED`/`NO_CHANGES` (`entrypoint.py:83-87`), so
  the job reads green while nothing happened.

Decisions (proposed defaults; adjust in review):

- **Job status:** keep `main()`'s exit code contract (red is an expected gate outcome) and surface red
  via a `$GITHUB_STEP_SUMMARY` line plus the artifact, rather than failing the job. A failing job is a
  follow-up option if red should page.
- **Playwright traces:** run the suite with `--tracing=retain-on-failure` and upload the traces, since a
  UI failure is fastest to read from a trace.
- **Retention:** leave `retain-days` unset (repo default).

Out of scope: changing the publisher or the merge gate, and dispatch-verifying the two ticket-06 items.
