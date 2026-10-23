# 24a-3: Resolve the Test Case and compute the verdict key

**What to build:** Add the pure part of `web_test/planning/verify.py`: given the changed paths, keep
only `test-case/test-case-*.md` artifacts, read the front-matter `id`, resolve `prd/<id>.md`, read
both texts, and compute `test_case_digest`, `prd_digest`, the question-set version, and the cache key.

**Blocked by:** None.

**Status:** ready-for-human

- [x] Only `test-case/test-case-*.md` artifacts are considered
- [x] Zero artifacts returns a "nothing to verify" outcome
- [x] More than one artifact returns an outcome listing the files
- [x] A missing `prd/<id>.md` returns a "missing PRD" outcome
- [x] Digests use `verification.digest_text` over the file contents
- [x] The question-set version comes from `questions_for_subject` + `question_set_version`
- [x] The key hashes `test_case_digest + prd_digest + question_set_version + JEV_MODEL + band values`
- [x] The same inputs produce the same key; changing either file or the question set changes it
- [x] Tests cover every outcome and the key stability
- [x] `uv run pytest`, `uv run basedpyright`, `uv run lint-imports` stay green

## Decisions / assumptions

- The key includes `prd_digest`; the verdict is bound to it even though the original 24a decision
  omitted it.
- No Jev call happens here; this is parse and hash only.
- Outcomes are typed (a small dataclass), not exceptions, so 24a-4 can map them to a payload.

**2026-10-21 — implemented.**

- `web_test/planning/verify.py`: `ResolutionKind`, `CheckInput`, `Resolution`, and
  `resolve(changed_paths, *, workspace)`.
- `resolve` filters artifact-shaped paths, returns `nothing` / `multiple` / `missing_prd` /
  `invalid` outcomes, and for one artifact reads the file and `prd/<front-matter id>.md`, computes
  both digests, the question-set version, and the key.
- The key is `SHA-256(test_case_digest + prd_digest + question_set_version + JEV_MODEL + band
  values)`.
- The artifact-shape check mirrors `automation.case_file` locally with a shortcut comment; importing
  `automation` from planning would add a use-case-to-use-case dependency.
- `_read_case` and `_read_prd` hold the two read phases; a PRD read failure maps to `INVALID` with
  `reading PRD <path> failed`.
- `tests/planning/test_verify.py`: 10 tests (nothing, ready + digests, multiple, missing PRD,
  unreadable PRD, no cases, no front matter, no id, key stability/sensitivity, question-set
  version).
- `uv run pytest`: 156 passed, 1 skipped. `uv run basedpyright`: 0 errors, 0 warnings.
  `uv run lint-imports`: 2 contracts kept.

**2026-10-23 — result slimmed.** `resolve` now only resolves files: `Resolution.texts` carries
`ResolvedTexts(test_case_text, prd_text)`; `TestCaseInput` and `PrdInput` were removed. The cache
key moved to `verify_key.py` (`cache_key`, `InvalidTestCase`), and its tests moved to
`test_verify_key.py`. 191 passed.

**2026-10-23 — tracker cleanup.** All acceptance items are checked; status moved to `ready-for-human`.
