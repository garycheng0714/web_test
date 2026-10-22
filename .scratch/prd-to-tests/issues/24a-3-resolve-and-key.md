# 24a-3: Resolve the Test Case and compute the verdict key

**What to build:** Add the pure part of `web_test/planning/verify.py`: given the changed paths, keep
only `test-case/test-case-*.md` artifacts, read the front-matter `id`, resolve `prd/<id>.md`, read
both texts, and compute `test_case_digest`, `prd_digest`, the question-set version, and the cache key.

**Blocked by:** None.

**Status:** ready-for-agent

- [ ] Only `test-case/test-case-*.md` artifacts are considered
- [ ] Zero artifacts returns a "nothing to verify" outcome
- [ ] More than one artifact returns an outcome listing the files
- [ ] A missing `prd/<id>.md` returns a "missing PRD" outcome
- [ ] Digests use `verification.digest_text` over the file contents
- [ ] The question-set version comes from `questions_for_subject` + `question_set_version`
- [ ] The key hashes `test_case_digest + prd_digest + question_set_version + JEV_MODEL + band values`
- [ ] The same inputs produce the same key; changing either file or the question set changes it
- [ ] Tests cover every outcome and the key stability
- [ ] `uv run pytest`, `uv run basedpyright`, `uv run lint-imports` stay green

## Decisions / assumptions

- The key includes `prd_digest`; the verdict is bound to it even though the original 24a decision
  omitted it.
- No Jev call happens here; this is parse and hash only.
- Outcomes are typed (a small dataclass), not exceptions, so 24a-4 can map them to a payload.
