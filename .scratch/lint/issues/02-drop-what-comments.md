# 02: Drop comments that restate the constants

**What to build:** Two constants added for `PLR2004` carry a comment that only repeats what the name
already says: `_STEP_COLUMNS` in `web_test/planning/review/parser.py` and `_CASE_MARKER_ARGS` in
`web_test/automation/quality.py`. Remove the comments, or rename the constants so the intent lives in
the name.

**Why:** project convention is to comment only the why the code cannot show.

**Status:** ready-for-agent

- [ ] The two constants no longer carry a what-comment
- [ ] `uv run ruff check` and `uv run pytest` stay green
