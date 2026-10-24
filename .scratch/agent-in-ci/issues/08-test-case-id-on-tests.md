# 08: Tag generated tests with the test-case id

**What to build:** Every generated Automation Test carries the source test-case file id and the
case number in a pytest marker, so the quality gate (ticket 10a) can map each test back to
`test-case/<file-id>.md` case N.

**Shape:**

- Marker: `@pytest.mark.case("<file-id>", <case-number>)` on every generated test function.
- `<file-id>` is the test-case front-matter `id`; `<case-number>` is the integer in the file's
  `## Case N:` heading.
- Registered in `pyproject.toml` under `[tool.pytest.ini_options].markers`.
- Required by the agent's `INSTRUCTIONS` and the `page-object-model` skill.
- Invariants: exactly one marker per test; one test maps to one case; every `## Case N` in the case
  file has at least one generated test with that marker.

**Blocked by:** None.

**Status:** ready-for-agent

- [ ] Every generated test function has exactly one `@pytest.mark.case("<file-id>", <n>)`
- [ ] The marker is registered in `pyproject.toml`
- [ ] The rule is in `INSTRUCTIONS` and the `page-object-model` skill
- [ ] Every `## Case N` in the case file has at least one generated test with that marker
- [ ] Unit-tested at the agent seam (instructions/skill contain the rule; the marker is parseable)

## Comments

Today the generated test carries no case id — PR #4's `tests/test_contact_us.py` is just
`def test_contact_us_form(...)`. The id only reaches the branch, commit message, and PR title
(`web_test/publishing/publish.py:9,13`).

Options (implementation details to decide later):

- **pytest marker** `@pytest.mark.case("test-case-0003")`, registered in `pyproject.toml`
  (`[tool.pytest.ini_options].markers`); selectable with `-m`.
- Test-function name including the id.
- Module docstring.

This is the still-open "priority/type emitted as test markers" from
`.scratch/prd-to-tests/issues/08-automate-command.md:16,28`. Whether to also carry `priority`,
`test_type`, and `requirement_ids` is open. Who writes it: the agent (instructions/skill), or the
entrypoint injecting the id deterministically.

**2026-10-24 — metadata.** 05 is done, so this is unblocked. It still needs the marker-vs-name-vs-docstring decision before implementation.

**2026-10-24 — parked.** No concrete consumer yet. The grill found that `pytest -m case` cannot
select by marker argument, `pytest -v` does not print marker arguments, the automation unit is one
file per PRD (so the same id would repeat on every test from that run), and this ticket does not
unblock tickets 10, 22b, or 09. Revisit when ticket 10's run report (or another concrete query)
needs the test→case mapping; the marker-vs-name-vs-docstring decision is deferred.

**2026-10-24 — unparked and re-scoped.** Consumer: the quality gate in ticket 10a. The marker
shape is decided: `@pytest.mark.case("<file-id>", <case-number>)`, one test per case. The earlier
park was because no consumer existed; the quality gate now needs the test→case mapping to catch a
missing case.
