# 01: Persist human adjudications as labels

**What to build:** When a reviewer approves a `NEEDS_REVIEW` or `BLOCKED` verdict with a reason,
the pipeline leaves a durable, append-only record of the original verdict, the published verdict,
the reason, the head SHA, and who approved it. An eval run can read those records without calling
GitHub. Today the override lives only in the check summary and is lost with it.

**Shape:**

- `Adjudication` — Pydantic boundary, written to disk: `head_sha`, `original`, `published`,
  `reason`, `reviewer`, `recorded_at`, `model`, `question_set_version`.
- `Approval` gains `reviewer` (the approving login); the workflow passes it through.
- Invariants: `head_sha` is the head being verified; `original` is `NEEDS_REVIEW` or `BLOCKED`;
  `reason` is non-empty after trimming; at most one record per head; append-only; no secret values.
- Boundary: the verification workflow writes; the eval reads.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] An approving review on a `NEEDS_REVIEW`/`BLOCKED` head appends exactly one record
- [ ] A `FAIL` approval is not recorded as an adjudication (it remains ignored)
- [ ] A record for an older head is not written
- [ ] The record is available as a CI artifact and in the ignored local verification directory
- [ ] Tests cover apply, ignore, head mismatch, and duplicate

## Decisions / assumptions

- The record is written after the check is published, so it can carry the final published status.
- The reviewer login is added to the existing approval boundary rather than read from the summary.
- A record is a label for calibration, not an authorization to skip the Gate.

## Out of scope

- Reading the labels back into an eval (ticket 04).
- Backfilling reviews that predate this ticket.
