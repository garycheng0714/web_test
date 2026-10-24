# 10b: Run report

**What to build:** Report the quality findings and the generated tests' pass/fail honestly. On a
block, write the report into `summary.md`/the artifact. On green, append a `## Run report` section to
the agent's PR body before publishing. List generated tests and every failing existing test; do not
list the ~255 passing existing tests.

**Shape:**

- `Suite.run()` adds `--junitxml=test-results/junit.xml`; parse it with `xml.etree.ElementTree`.
- `TestOutcome` (frozen dataclass): `nodeid`, `outcome` (`passed`/`failed`), `message`.
- `RunReport` (frozen dataclass): quality findings, generated outcomes, failing existing outcomes.
- `AutomationEvidence.report: RunReport | None`.
- Invariants: the report never changes the gate; a missing or malformed JUnit file is reported as
  unavailable, not fatal; generated tests are identified by the changed paths under `tests/`.

**Module plan — `web_test/automation/report.py`:**

1. **Input:** JUnit XML, generated paths, quality findings.
2. **Output:** `RunReport` and rendered markdown.
3. **External boundaries:** the filesystem XML only.
4. **Domain types vs adapters:** `TestOutcome`/`RunReport` are domain data; the XML parser is the
   adapter.
5. **Single-variation parts:** the quality rules, gate, and publisher are untouched.
6. **Responsibilities:** read the JUnit result and render the run report.

**Blocked by:** 10a.

**Status:** ready-for-agent

- [ ] `Suite.run()` writes `test-results/junit.xml`
- [ ] JUnit parsing is unit-tested for pass/fail and missing/malformed XML
- [ ] The report lists generated tests' pass/fail and every failing existing test
- [ ] Passing existing tests are not listed
- [ ] A block writes the report into the evidence summary/artifact
- [ ] A green run appends `## Run report` to the PR body before publishing
- [ ] `uv run pytest`, `uv run basedpyright`, `uv run ruff check --select F401`,
      `uv run lint-imports`, and `actionlint` pass

## Out of scope

- Fixme markers and `skip`/`xfail` reasons.
- The `playwright-cli` tool-name rule.
- Listing every passing existing test.
- Changing the gate or the quality rules from 10a.
