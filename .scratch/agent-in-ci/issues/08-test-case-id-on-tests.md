# 08: Tag generated tests with the test-case id

**What to build:** Every generated Automation Test carries the id of the `test-case/<id>.md` it came
from, so a test (and its CI output) is traceable back to its source case.

**Blocked by:** None (05 complete).

**Status:** needs-triage

- [ ] Generated tests expose their source case id in a machine-readable form
- [ ] The id is selectable from the test run (e.g. a `pytest` marker, or visible in `pytest -v`)
- [ ] The requirement lives in the agent's `INSTRUCTIONS` and the `page-object-model` skill
- [ ] Unit-tested at the agent seam

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
