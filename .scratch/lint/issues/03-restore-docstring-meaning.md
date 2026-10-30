# 03: Restore the meaning the E501 rewrites dropped

**What to build:** Three docstrings were shortened to fit the 100-character limit and lost meaning in
the process. Reword them so the original sense survives while staying within the limit.

- `web_test/planning/cases_writer.py:84` (`render_document`): "a title, one section per case, open
  questions" reads as four items and drops the "and".
- `web_test/planning/cases_writer.py:92` (`CaseWriter`): "overwriting it" no longer says what is
  overwritten.
- `web_test/planning/review/jev.py:38` (`typesafe_system_one`): dropped "with the built request" and
  the fact that the environment variables are read.

**Invariants:** no behavioural change; keep each docstring on one line at 100 characters or wrap it.

**Status:** ready-for-agent

- [ ] The three docstrings say what they said before the E501 pass
- [ ] `uv run ruff check` and `uv run ruff format --check` stay green
