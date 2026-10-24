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

**Status:** ready-for-agent

- [ ] One helper owns the absolute/`..`/suffix/resolve/inside-workspace/file checks
- [ ] `quality` still reads only `.py`; evidence still copies `.py` and `.zip` only
- [ ] Tests cover absolute, `..`, wrong suffix, symlink-outside-workspace, and missing paths
- [ ] `uv run pytest`, `uv run basedpyright`, `uv run ruff check --select F401`,
      `uv run lint-imports`, and `actionlint` pass

## Notes

This is a polish finding from the 10a review, not a behavior change. The duplicated shape is at
`web_test/automation/quality.py:50`, `web_test/automation/evidence.py:137`, and
`web_test/automation/evidence.py:163`.
