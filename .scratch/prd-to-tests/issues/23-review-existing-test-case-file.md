# 23: Review an existing Test Case file

**What to build:** A local command that reads a Test Case markdown file back into step-level review
state and reruns the same Jev verification used during Plan. It always reviews the current file
contents; no digest or stale comparison is performed.

**Blocked by:** 21 (the review engine and record).

**Status:** needs-triage

- [x] A file produced by Plan round-trips back into step-level review state
- [x] The parsed state preserves each step's action and expected result
- [x] Editing a case, step, or expected result changes the input sent to Jev
- [x] The command is read-only and usable outside CI
- [x] Tests cover the round trip, an edit, a review run, and a CLI error path

## Comments

**2026-10-21 — implemented.**

- Added `web_test/planning/review/parser.py`: `parse_test_case(text, prd_text)` reads `## Case N`
  sections, the YAML metadata block, and the `### Test Steps` table back into `ReviewSubject`.
- Added `web_test/planning/review/local.py`: `review_case_file(case_path, prd_path, ...)` reads the
  files and always reviews the current contents with `run_review_on`.
- Added `web_test/planning/review/cli.py`:
  `uv run python -m web_test.planning.review.cli --case <path> --prd <path>`.
- Stale/digest comparison was removed: the command always produces a fresh verdict for the current
  file. `VerificationRecord.binding.test_case_digest` remains available for manual comparison.
- Tests: `tests/planning/test_review_parser.py` (round trip, edit) and
  `tests/planning/test_review_local.py` (review run, edited step reaches Jev, CLI error).
- `uv run pytest`: 132 passed, 1 skipped.
