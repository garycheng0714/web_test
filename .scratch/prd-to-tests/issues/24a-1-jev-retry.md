# 24a-1: Add a Jev retry seam

**What to build:** Add `retry_once(system_one: SystemOne) -> SystemOne` to
`web_test/planning/review/jev.py`. The wrapper retries the Jev call once when it raises or returns an
empty mapping. `typesafe_system_one` stays a single-shot call; only the verification check (24a-4)
composes the retry.

**Blocked by:** None.

**Status:** ready-for-agent

- [ ] The factory returns a `SystemOne` with the same signature
- [ ] A raised exception triggers exactly one retry
- [ ] A second exception propagates unchanged
- [ ] An empty answer mapping triggers exactly one retry
- [ ] A second empty mapping is returned unchanged
- [ ] Non-empty answers are returned without a retry
- [ ] `typesafe_system_one` still makes a single call
- [ ] Tests cover each path and assert the call count
- [ ] Ticket 19's Authority wording matches the policy
- [ ] `uv run pytest`, `uv run basedpyright`, `uv run lint-imports` stay green

## Decisions / assumptions

- One retry, no backoff.
- Catch `Exception`, not `BaseException`.
- Partial answers are not a retry reason; only an exception or an empty mapping is.
- The wrapper lives in `jev.py` because retry is part of "how to call Jev", not part of the check.

## Comments

Ticket 19 originally said `BLOCKED` retries once. That is narrowed to "a failed Jev call or an empty
answer" because `request build failed` and partial answers are deterministic. The check (24a-4)
composes this wrapper; `typesafe_system_one` and the other callers keep their single-shot behavior.
