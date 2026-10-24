# 18: Share the workspace path guard

**What to build:** Extract the repeated "relative path → safe resolve → inside workspace" predicate
into one helper. The three callers keep their own behavior: `quality._source_path` reads `.py`,
`evidence._copy_generated` copies `.py`, and `evidence._copy_trace` copies `.zip`.

**Shape:**

- `resolve_workspace_path(workspace: Path, relative: str, *, suffix: str) -> Path | None` in
  `web_test/write_guard.py` (the existing path-guard module).
- Invariant: returns a path only when it is relative, has no `..`, has the expected suffix, resolves
  inside the workspace, and is an existing file; otherwise `None`.
- No caller behavior changes; no new module.

**Blocked by:** None.

**Status:** ready-for-human (done; implemented)

- [x] One helper owns the absolute/`..`/suffix/resolve/inside-workspace/file checks
- [x] `quality` still reads only `.py`; evidence still copies `.py` and `.zip` only
- [x] Tests cover absolute, `..`, wrong suffix, symlink-outside-workspace, and missing paths
- [x] `uv run pytest`, `uv run basedpyright`, `uv run ruff check --select F401`,
      `uv run lint-imports`, and `actionlint` pass

## Notes

This is a polish finding from the 10a review, not a behavior change. The duplicated shape was at
`web_test/automation/quality.py:52`, `web_test/automation/evidence.py:141`, and
`web_test/automation/evidence.py:167`.

**2026-10-25 — implemented.**

- `web_test/write_guard.py`: `resolve_workspace_path(workspace, relative, *, suffix)` owns the
  absolute/`..`/suffix/resolve/inside-workspace/file checks.
- `quality.py` calls it with `.py`; `_source_path` is gone.
- `evidence._copy_generated` / `_copy_trace` call it with `.py` / `.zip` and keep their
  `ALLOWED_DIRS` / `test-results` checks.
- `tests/test_write_guard.py` covers the happy path, nested paths, absolute, `..`, wrong suffix,
  missing files, and a symlink outside the workspace.
- `uv run pytest`: 304 passed, 1 skipped; basedpyright, ruff F401, lint-imports, and actionlint are
  green.
