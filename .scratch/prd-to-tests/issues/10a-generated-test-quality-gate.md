# 10a: Generated-test quality gate

**What to build:** After the coding agent returns and before the suite runs, check the generated
tests against deterministic quality rules. A finding blocks the run: no PR, `QUALITY_RED`, exit 1,
and the findings go into the evidence summary/artifact. There is no agent repair chance.

**Shape:**

- `QualityFinding` (frozen dataclass): `rule: QualityRule`, `detail`.
- `QualityRule` (`StrEnum`): the seven closed rule ids.
- `AutomationEvidence.quality: tuple[QualityFinding, ...] = ()`.
- `AutomationStatus.QUALITY_RED = "quality_red"`; `exit_code()` returns 1 (the existing red mapping).
- Invariants: findings block publish; the gate runs after the agent returns and before `suite.run()`;
  `AGENT_RED` keeps precedence over `QUALITY_RED`; a clean generated set produces no findings.

Rules in this slice:

1. Every `## Case N:` in the case file has at least one generated test whose
   `@pytest.mark.case("<file-id>", <n>)` marker matches it; a marker for a case that does not exist
   is a finding; a generated test with no marker is a finding (ticket 08's one-marker invariant).
2. Every generated test has at least one `assert` or `expect(...)`.
3. Generated tests contain no selectors or `page.goto`; they must use page objects.
4. Generated test files live under `tests/` and import `pages`/`components`.

**Module plan — `web_test/automation/quality.py`:**

1. **Input:** case id, raw case text, generated paths, workspace.
2. **Output:** `tuple[QualityFinding, ...]`.
3. **External boundaries:** reads generated `.py` files; no git, model, network, or browser.
4. **Domain types vs adapters:** `QualityFinding` is domain data; AST and file reading stay in this
   module.
5. **Single-variation parts:** the agent, repair guard, suite, and publisher are untouched.
6. **Responsibilities:** deterministic generated-test quality rules; one reason to change.

## Responsibilities

```text
quality.py
  │
  ├── domain types ────────── QualityRule, QualityFinding
  │     change reason: the finding/rule vocabulary
  │
  ├── rule detectors ──────── one detector per rule
  │     _case_numbers, _test_functions, _markers, _is_page,
  │     _direct_page_calls, _asserts, _imports_page_objects
  │     change reason: how one rule is decided
  │
  ├── orchestrator ────────── quality_findings (public seam)
  │     change reason: rule composition / blocking order
  │
  └── path safety ─────────── _source_path  (foreign; ticket 18)
        change reason: the path-guard policy
```

`_source_path` is the one exception to "one reason to change": it is a path guard, not a quality
rule, and moves to `write_guard.py` in ticket 18. `_where` is formatting, not a responsibility.

**Blocked by:** None (agent-in-ci 08 is complete).

**Status:** ready-for-human (done; implemented)

- [x] Every `## Case N` is covered by a matching marker, and unknown/unmarked markers are findings
- [x] Every generated test asserts through `assert` or `expect(...)`
- [x] Generated tests contain no direct `page` selector/`goto` calls
- [x] Generated test files are under `tests/` and import `pages`/`components`
- [x] Findings set `QUALITY_RED`, skip the suite and the PR, and appear in the evidence summary
- [x] Tests cover each rule and the entrypoint block
- [x] `uv run pytest`, `uv run basedpyright`, `uv run ruff check --select F401`,
      `uv run lint-imports`, and `actionlint` pass

## Decisions / assumptions

- The rule set is a `QualityRule` `StrEnum`, per the closed-set convention in `AGENTS.md`.
- Rule 1 also requires a marker on every generated test. Ticket 08 says exactly one per test; this
  makes the mapping check meaningful.
- Rule 2 counts Playwright's imported `expect(...)` function and `assert`; `.expect(...)` is not a
  Playwright method and is not treated as an assertion.
- Rule 3 only flags direct calls on a `page` receiver: `goto`, `locator`, `get_by_*`, and
  `query_selector*`. `page.on`, `page.wait_for_load_state`, `expect`, and page-object calls are
  allowed.
- Rule 4 applies to files that contain `test_*` functions. A page object with no tests is not a
  generated test file.
- `AGENT_RED` keeps precedence: the gate runs only when the agent returned a PR body. A red agent
  run already publishes nothing.
- Deleted paths are skipped; an unparseable generated file is a finding rather than a crash.

## Out of scope

- The run report; that is 10b.
- A `skip`/`xfail` reason rule and a `playwright-cli` tool-name rule (deferred).
- Fixme markers for non-automatable cases.
- Giving the agent a repair chance after a quality finding (block immediately).

**2026-10-24 — implemented.**

- `web_test/automation/quality.py`: `QualityRule` (`StrEnum`), `QualityFinding`, and
  `quality_findings`; AST rules for case markers/coverage, assertions, direct `page`
  selectors/`goto`, test location, and page-object imports.
- `web_test/automation/entrypoint.py`: `QUALITY_RED`; the gate runs after the `AGENT_RED` check and
  before `suite.run()`, and blocks the suite and the PR.
- `web_test/automation/evidence.py`: `AutomationEvidence.quality` and a `### Quality gate` section
  in the summary/artifact.
- `README.md`: `QUALITY_RED` and the findings are listed with the red-run evidence.
- `uv run pytest`: 283 passed, 1 skipped; basedpyright, ruff F401, lint-imports, and actionlint are
  green.
