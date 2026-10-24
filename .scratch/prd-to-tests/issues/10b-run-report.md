# 10b: Run report

**What to build:** Report the quality findings and the generated tests' pass/fail honestly. On a
block, write the report into `summary.md`/the artifact. On green, append a `## Run report` section to
the agent's PR body before publishing. List generated tests and every failing existing test; do not
list the ~255 passing existing tests.

**Shape:**

- `Suite.run()` adds `--junitxml=test-results/junit.xml`; parse it with `xml.etree.ElementTree`.
- `TestStatus` (`StrEnum`): `PASSED`, `FAILED`, `SKIPPED`. `<failure>` and `<error>` map to
  `FAILED`; an existing skipped test is not a failure.
- `TestOutcome` (frozen dataclass): `nodeid`, `file`, `status`, `message`.
- `RunReport` (frozen dataclass): `generated`, `failing`, `junit_available`.
- `AutomationEvidence.report: RunReport | None`; quality findings stay in
  `AutomationEvidence.quality`, because quality and JUnit results are mutually exclusive (the gate
  blocks before the suite).
- Invariants: the report never changes the gate; a missing or malformed JUnit file is reported as
  unavailable, not fatal; generated tests are identified by the changed paths under `tests/`.

**Module plan — `web_test/automation/report.py`:**

1. **Input:** JUnit XML text or path, generated paths.
2. **Output:** `RunReport` and rendered markdown.
3. **External boundaries:** the filesystem XML only.
4. **Domain types vs adapters:** `TestOutcome`/`RunReport` are domain data; `parse_junit` is the
   pure parser and `read_junit` the best-effort file adapter.
5. **Single-variation parts:** the quality rules, gate, and publisher are untouched.
6. **Responsibilities:** read the JUnit result, classify it, and render the run report.

**Blocked by:** 10a (done; merged in #34).

**Status:** ready-for-human (done; implemented)

- [x] `Suite.run()` writes `test-results/junit.xml`
- [x] JUnit parsing is unit-tested for pass/fail and missing/malformed XML
- [x] The report lists generated tests' pass/fail and every failing existing test
- [x] Passing existing tests are not listed
- [x] A block writes the report into the evidence summary/artifact
- [x] A green run appends `## Run report` to the PR body before publishing
- [x] `uv run pytest`, `uv run basedpyright`, `uv run ruff check --select F401`,
      `uv run lint-imports`, and `actionlint` pass

## Decisions / assumptions

- Generated tests are the changed paths under `tests/`; the predicate is shared with 10a in
  `write_guard.is_generated_test_path`.
- A generated `SKIPPED` test is listed (honesty); an existing `SKIPPED` test is not a failure and is
  not listed.
- A failure message is the first line, capped at 200 characters; the full traceback stays in the
  suite output/evidence.
- Pytest's default JUnit family (`xunit1`) includes the `file` attribute, which is what maps a
  `testcase` back to a changed path.
- On green the report is appended to the PR body; on `SUITE_RED` / `NO_CHANGES` it goes to the
  evidence summary/artifact. `QUALITY_RED` / `AGENT_RED` have no JUnit run.

## Out of scope

- Fixme markers and `skip`/`xfail` reasons.
- The `playwright-cli` tool-name rule.
- Listing every passing existing test.
- Changing the gate or the quality rules from 10a.

**2026-10-25 — implemented.**

- `web_test/publishing/suite.py`: adds `--junitxml=test-results/junit.xml` and exposes `JUNIT_XML`.
- `web_test/automation/report.py`: `TestStatus`, `TestOutcome`, `RunReport`, `parse_junit`,
  `read_junit`, `build_run_report`, and `render_run_report`. Generated skipped tests are shown;
  existing skipped/passing tests are omitted. Failure messages are the first line, capped at 200
  characters.
- `web_test/automation/entrypoint.py`: reads the JUnit file after the suite, stores the report in
  the evidence, and appends `## Run report` to the PR body before publishing. A missing JUnit file
  renders as unavailable and does not change the gate.
- `web_test/automation/evidence.py`: `AutomationEvidence.report` and the summary section.
- `web_test/write_guard.py`: `is_generated_test_path`, shared with the quality gate.
- `uv run pytest`: 295 passed, 1 skipped; basedpyright, ruff F401, lint-imports, and actionlint are
  green.
