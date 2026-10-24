# 16: Playwright traces in red-run evidence

**What to build:** Add the Playwright trace of a failing UI test to the red-run evidence. Today the
`automation-evidence-*` artifact holds the pytest/suite output, the tool trace, and the generated
files, but not a browser trace, which is the fastest way to read a UI failure. Split out of ticket
07 (`.`scratch/agent-in-ci/issues/07-red-run-evidence.md`); the gate stays unchanged.

**Blocked by:** 07 (live-run verified).

**Status:** ready-for-agent

- [ ] The suite runs with `--tracing=retain-on-failure` (`pytest-playwright`'s option)
- [ ] The resulting traces (default `test-results/`) reach the uploaded artifact, either copied by
      `automation/evidence.py` or uploaded as a separate path
- [ ] `.playwright-cli/` and `.venv` stay out of the artifact
- [ ] The summary says when no trace was produced (green run or tracing unavailable)
- [ ] Unit-tested through the evidence writer's real seam

## Notes

`automation/evidence.py` currently copies only `.py` files under `tests/`, `pages/`, and
`components/` (`web_test/write_guard.py` `ALLOWED_DIRS`). A trace is a `.zip` in `test-results/`, so
the allowed-path rule must be widened deliberately, not by copying the whole workspace.
