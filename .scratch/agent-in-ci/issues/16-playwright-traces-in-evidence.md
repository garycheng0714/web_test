# 16: Playwright traces in red-run evidence

**What to build:** Add the Playwright trace of a failing UI test to the red-run evidence. Today the
`automation-evidence-*` artifact holds the pytest/suite output, the tool trace, and the generated
files, but not a browser trace, which is the fastest way to read a UI failure. Split out of ticket
07 (`.`scratch/agent-in-ci/issues/07-red-run-evidence.md`); the gate stays unchanged.

**Blocked by:** 07 (live-run verified).

**Status:** ready-for-human (done; implemented)

- [x] The suite runs with `--tracing=retain-on-failure` (`pytest-playwright`'s option)
- [x] The resulting traces (default `test-results/`) reach the uploaded artifact, either copied by
      `automation/evidence.py` or uploaded as a separate path
- [x] `.playwright-cli/` and `.venv` stay out of the artifact
- [x] The summary says when no trace was produced (green run or tracing unavailable)
- [x] Unit-tested through the evidence writer's real seam

## Notes

`automation/evidence.py` currently copies only `.py` files under `tests/`, `pages/`, and
`components/` (`web_test/write_guard.py` `ALLOWED_DIRS`). A trace is a `.zip` in `test-results/`, so
the allowed-path rule must be widened deliberately, not by copying the whole workspace.

**2026-10-24 — implemented.**

- `Suite.run()` now runs `uv run pytest -q --tracing=retain-on-failure --output=test-results/suite`.
  The suite's traces are isolated under `test-results/suite/`; any traces the agent produced itself
  are still picked up.
- `automation/evidence.py` gained `collect_traces()` and `AutomationEvidence.traces` /
  `traces_skipped`. It copies only `test-results/**/*.zip` (no absolute paths, `..`, symlinks out of
  the workspace, `.venv`, or `.playwright-cli`) into `traces/` under the evidence directory.
- The artifact is capped at **20 files / 50MB** per run; skipped traces are counted in the summary.
- `render_summary()` adds a `### Traces` section and says `no trace produced` when there are none.
- `test-results/` is gitignored; the README describes the Playwright traces.
- Unit-tested: `test_suite.py` asserts the flags; `test_evidence.py` covers copying, exclusions, the
  file/byte caps, and the summary; `test_entrypoint.py` covers trace capture on a red outcome.
- Not live-run: producing a trace needs `SUITE_RED` (the agent returns a body but the suite is red);
  the throwaway red fixture tends to end `AGENT_RED` with no suite run. The next real `SUITE_RED`
  will exercise it.
