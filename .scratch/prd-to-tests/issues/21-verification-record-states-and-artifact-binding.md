# 21: Record verification state and bind it to the artifact

**What to build:** Plan and the reviewer emit a typed verification record instead of `None` or a
free-form report string. The record carries the verdict (`PASS`, `NEEDS_REVIEW`, `FAIL`, `BLOCKED`)
at step, case, and file level, the PRD digest, the Test Case artifact digest, the verifier model,
the question-set version, and the bands. The PR body always shows a status; when Jev is unavailable
it says `BLOCKED` instead of omitting the section. A record can also carry an adjudication override:
the original verdict, the reason, and the head it applied to.

**Blocked by:** 19 (the contract fixes the vocabulary and authority).

**Status:** ready-for-human (done; implemented)

- [x] The record models `PASS`, `NEEDS_REVIEW`, `FAIL`, and `BLOCKED` at step, case, and file level
- [x] Aggregation follows `FAIL > BLOCKED > NEEDS_REVIEW > PASS`
- [x] A missing answer is `BLOCKED`, never a pass
- [x] The PR body renders a status even when verification is unavailable
- [x] The record stores PRD and artifact digests plus model, question-set, and band versions
- [x] The record can represent an override with its original verdict, reason, and head SHA
- [x] Re-rendering the same inputs yields the same digests and verdict
- [x] Plan still opens the PR; the required check is ticket 24a/24b
- [x] Tests cover each verdict, the unavailable path, and the aggregation precedence

## Comments

**2026-10-20 — implemented.**

- Added `web_test/planning/verification.py`: `VerdictStatus`, `Bands`, `CheckOutcome`,
  `UnitOutcome`, `Override`, `VerificationRecord`, `worst`, and `digest_text`.
- Split review models into `review_subject.py` and prompt text, IDs, and expected checks into
  `review_questions.py`; `review.py` now only builds requests, aggregates answers, and runs Jev.
- `review.py` now builds step, case, and file verdicts with `FAIL > BLOCKED > NEEDS_REVIEW > PASS`,
  binds PRD/artifact digests, model, question-set version, and bands, and returns a `BLOCKED`
  record on failure instead of `None`.
- `review_report.py` always renders the status, counts, findings, needs review, blocked reason,
  evidence, and override.
- `entrypoint.py` renders the artifact before review and writes the same content, so the artifact
  digest matches the file.
- Follow-up: all-blocked records carry a reason, question-set-version failures return `BLOCKED`,
  and the publisher passes `content` explicitly.
- `uv run pytest`: 117 passed, 1 skipped.

**2026-10-23 — tracker cleanup.** All acceptance items are checked; status moved to
`ready-for-human`.

**2026-10-24 — bookkeeping: done.**

`web_test/planning/review/record.py` records the verification state and binds it to the artifact. Status → `ready-for-human (done; implemented)`.
