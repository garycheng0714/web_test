# 01: Make the coverage mutation in the quality checks visible

**What to build:** `_function_findings` in `web_test/automation/quality.py` returns a list of findings
but also mutates the `covered` set passed in by `quality_findings`. Make that effect visible: either
return the covered case numbers and let `quality_findings` merge them, or rename the helper so its
name states that it also records coverage.

**Invariants:** the order, wording, and content of the findings stay identical; every case-coverage
finding still points at cases that no test claimed.

**Status:** ready-for-agent

- [ ] `_function_findings` no longer hides a mutation behind a "findings" name
- [ ] `tests/automation/test_quality.py` stays green
- [ ] `uv run ruff check` and `uv run basedpyright` stay green
