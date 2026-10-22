# 24a-1: Add a Jev retry seam

**Superseded:** the TypeSafe SDK already retries HTTP failures through `RetryPolicy`
(`max_retries=2` by default, with backoff and `Retry-After`). No wrapper is added; an empty answer is
`BLOCKED` and is not retried.

**Blocked by:** None.

**Status:** wontfix

- [x] Confirmed the SDK retries HTTP 408/429/5xx, connection errors, and timeouts by default
- [x] Confirmed the default policy is 2 retries with backoff and a 30 s budget
- [x] Decided not to add a second retry layer, which would double the HTTP attempts
- [x] Empty answers are not retried; they publish `BLOCKED`
- [x] Removed the uncommitted `with_retry` probe and its tests
- [x] Updated ticket 19 and the 24a umbrella wording

## Decisions / assumptions

- HTTP retry is the SDK's responsibility, not the check's.
- The SDK default (`max_retries=2`, 3 attempts total) is kept; 3 retries would need
  `RetryPolicy(max_retries=3)`, which is not requested.
- The SDK handles backoff, jitter, `Retry-After`, 408/429/5xx, connection errors, and timeouts.
  Non-HTTP errors propagate immediately.
- An empty answer is a successful call with no answers; it is not a transport failure, so it is not
  retried.

## Comments

The first draft of this ticket added `with_retry(system_one, *, attempts=2)` to `jev.py`. Reading the
SDK showed that `AsyncTypeSafeClient()` already builds a tenacity policy with
`RetryPolicy(max_retries=2)`, so the wrapper would have produced up to 6 HTTP attempts instead of 3.
The wrapper and its tests were removed before commit.

Ticket 19's Authority line now says HTTP failures are retried by the SDK and an empty answer is
`BLOCKED`.
