# 07: Gate

**What to build:** The human approval gate as a state on the test-case artifact plus a reusable
check. Approval is expressed by editing the artifact's front-matter `approval` line (no separate
command).

**Blocked by:** 05

**Status:** ready-for-human

- [x] The test-case document carries an explicit approval state with defined values (`draft` → `approved`)
- [x] A pure function reports whether the document is approved
- [x] The function's behavior is unit-tested for both states
- [x] Approval by editing the state line is documented

## Comments

The qa table has its own per-case `status` column (`NotRun`…); the document-level gate uses a
separate front-matter field to avoid the collision:

```yaml
---
approval: draft   # draft | approved
---
```

- `web_test/document.py` — `is_approved(path)` reads the front-matter and returns a bool (pure,
  unit-tested for both states).
- `write_report()` refuses to overwrite an `approved` file unless `force=True`, so re-running the
  designer cannot silently discard a human approval.

Implemented together with ticket 05. `uv run pytest`: 12 passed, 1 failed (pre-existing header PUA).
