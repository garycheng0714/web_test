# 10: Make the automation branch name collision-resistant

**What to build:** A branch created for a case does not collide with an existing one when the same
case is run again.

**Blocked by:** 05 Automation entrypoint and approval gate.

**Status:** ready-for-human (done; run-scoped names)

- [x] Re-running the same case never fails on a non-fast-forward push
- [x] The name still identifies the case
- [x] Unit-tested (`branch_name`)

## Comments

`branch_name(case_id) = f"automation/{case_id}"` (`web_test/publishing/publish.py:9`). Observed: after
the run for `test-case-0002` left an orphan branch, a re-run of the same id could not push
(non-fast-forward; see ticket 06's dispatch notes). Case ids are assigned by scanning `test-case/`
(`.scratch/prd-to-tests/issues/06-plan-cli.md:13`), so ids themselves can also repeat.

Options (implementation details to decide later):

- Append the source merge short sha: `automation/<id>-<sha7>`.
- Append the run id / attempt.
- Append a date (ticket 02 originally said "branch named from the feature and date").

Interacts with 09: there, an update targets the existing PR's head branch rather than creating a new
one, so "unique on creation" is enough.

**2026-10-24 — bookkeeping: done.**

`web_test/naming.py` appends the run id/attempt (or a UTC timestamp locally) to every branch; `branch_name` and `run_token` are unit-tested in `tests/test_naming.py` and `tests/publishing/test_publish.py`. Status → `ready-for-human (done; run-scoped names)`.
