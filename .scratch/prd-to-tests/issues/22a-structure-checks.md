# 22a: Deterministic artifact structure checks

**What to build:** Run structural checks that need only the Test Case artifact before Jev, put the
results in the same verification record, and render them in the same check summary and PR body. A
structural failure is `FAIL` and cannot be adjudicated away.

Checks in this slice:

- front matter has a string `id`
- front matter has a string `base_url`
- case numbers are unique
- every case has at least one step
- every step has a non-empty action and expected result

**Shape:**

- `DeterministicOutcome` (frozen dataclass): `check_id`, `label`, `status`, `detail`.
  Invariant: `status` is only `PASS` or `FAIL`.
- `VerificationResult.structure: tuple[DeterministicOutcome, ...]` and `jev_status`; the final
  `status` is `worst(jev_status, *structure statuses)`.
- `VerificationBinding.check_set_version: str`; the cache key includes it.
- `CHECK_SET_VERSION` lives with the rules and is bumped whenever a deterministic rule changes.
- `CheckOutcome` and the Jev bands are unchanged.

**Module plan — `web_test/planning/review/structure.py`:**

1. **Input:** `ReviewSubject` and the raw Test Case text.
2. **Output:** `tuple[DeterministicOutcome, ...]`.
3. **External boundaries:** none; pure functions, no network or model.
4. **Domain types vs adapters:** domain module; `DeterministicOutcome` lives in
   `review/verification.py`.
5. **Single-variation parts:** Jev questions, bands, model, and Jev aggregation are untouched.
6. **Responsibilities:** structural validation rules and `CHECK_SET_VERSION`; one reason to change.

**Blocked by:** None (21 and 24b are complete).

**Status:** ready-for-human (done; implemented)

- [x] Front matter `id` and `base_url` are checked
- [x] Case numbers are checked for duplicates
- [x] Every case is checked for at least one step
- [x] Every step is checked for non-empty action and expected result
- [x] Results are stored in `VerificationResult.structure`; final status combines Jev and structure
- [x] A structure failure is `FAIL` and approval cannot override it
- [x] `CHECK_SET_VERSION` is in the cache key and in the verdict evidence
- [x] The check summary and Plan PR body render a `## Structure` section and a separate Jev status
- [x] Text without a rendered `## Case` section has no structure checks (synthetic/eval reviews)
- [x] Tests cover every check and the clean case
- [x] `uv run pytest`, `uv run basedpyright`, `uv run lint-imports`, `uv run ruff check --select
      F401`, and `actionlint` pass

## Decisions / assumptions

- Structure checks run only when the text contains a rendered `## Case` section. The eval harness
  and the synthetic review tests pass JSON or plain strings; those are not artifacts, so they keep
  their Jev-only behavior.
- Unparsable artifacts keep the existing early `INVALID` path. A Test Case with no cases cannot be
  parsed, so it never reaches this layer.
- The report shows the final `**Status:**`, a `## Structure` section, and a separate
  `**Jev status:**`. The check title remains the final status.
- The cache entry stores the final status; a structural `FAIL` is cached like any other `FAIL`.

## Out of scope

- Required case metadata (`priority`, `test_type`, `severity`).
- Requirement-to-case coverage and happy-path cases; that is 22b.
- Reporting an unparsable artifact in the same record.
- Any change to Jev questions, bands, or the adjudication authority.

## Comments

**2026-10-23 — implemented.**

- `review/structure.py`: `structure_checks` and `CHECK_SET_VERSION = "structure-v1"`.
- `review/verification.py`: `DeterministicOutcome`, `VerificationResult.structure`/`jev_status`,
  `VerificationBinding.check_set_version`.
- `review/record.py`: final status is `worst(jev_status, *structure)`; a structure `FAIL` is not
  masked by a blocked Jev review.
- `review/service.py`: structure checks run next to Jev; a Jev failure still carries the structure
  result.
- `review/report.py`: final status, `## Structure`, and `**Jev status:**`; check-set evidence.
- `verify/key.py`: `check_set_version` is part of the cache key.
- `README.md`: the required check now mentions deterministic structure checks.
- `uv run pytest`: 228 passed, 1 skipped; basedpyright, lint-imports, ruff F401, and actionlint are
  green.

**2026-10-24 — bookkeeping: done.**

`web_test/planning/review/structure.py` implements the deterministic checks; `CHECK_SET_VERSION = "structure-v1"`. Status → `ready-for-human (done; implemented)`.
