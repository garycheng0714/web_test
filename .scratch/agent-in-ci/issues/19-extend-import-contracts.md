# 19: Extend the import contracts to the full dependency graph

**What to build:** Ticket 12 added two contracts. Add the missing directions so the layering is
enforced, not just conventional. No production code change unless a contract exposes a real
violation.

Contracts to add:

- `web_test.publishing` is a leaf: it must not import `web_test.planning` or `web_test.automation`.
- `web_test.planning.schema` is a leaf: it must not import `web_test.planning.**`,
  `web_test.publishing`, or `web_test.automation` (extends the existing schema contract; `**`
  covers every planning sibling).
- `web_test.planning` does not import `web_test.automation` (replaces the narrower review-only
  contract).
- `web_test.planning.review` does not import `web_test.planning.verify`.
- `web_test.automation` imports only `web_test.planning.schema` from planning: forbid
  `web_test.planning.**` and ignore the one allowed `schema` edge.

## Why

Shared modules (`planning.schema`, `publishing`) are leaves: a leaf that imports a use case creates
cycles (`planning.review.service` already imports `schema`) and pulls model/client dependencies into
the other stage. See `docs/adr/0009-shared-modules-are-leaves.md`.

**Shape:** only `[tool.importlinter]` contracts in `pyproject.toml`. Invariant: the baseline passes
with 0 broken; a failing contract is a real dependency to fix, not a reason to weaken the rule.

**Blocked by:** None.

**Status:** ready-for-human (done; implemented)

- [x] The five directions above are enforced by `forbidden` contracts
- [x] `uv run lint-imports` passes (record the file/dependency count)
- [x] If any new contract fails, record the actual import in this ticket instead of relaxing it
- [x] The `contracts` CI job needs no change and stays green
- [x] `uv run pytest`, `uv run basedpyright`, `uv run ruff check --select F401`, and `actionlint` pass

## Decisions

- Keep `forbidden` contracts rather than a `layers` contract: the graph is a DAG, not a single
  linear chain, and `forbidden` already produces the useful error message.
- Replacing the review-only contract with the planning-wide one avoids a redundant contract while
  keeping the same guarantee.
- Keep the separate review-not-verify contract: the error message names the exact direction.

## Out of scope

- Moving shared modules (`command`, `naming`, `paths`, `write_guard`, `observability`, `model`) into
  a `web_test.shared` package.
- Changing `publishing`'s API or its callers.

**2026-10-25 — implemented.**

- `pyproject.toml` now has five `forbidden` contracts:
  - schema → `web_test.planning.**`, `web_test.publishing`, `web_test.automation`
  - planning → automation
  - review → verify
  - publishing → planning, automation
  - automation → `web_test.planning.**`, with the one allowed
    `web_test.automation.** -> web_test.planning.schema` import ignored
- `uv run lint-imports`: 53 files, 131 dependencies, 5 contracts kept, 0 broken, 1 ignored import.
- The schema contract uses `web_test.planning.**` instead of listing siblings: every planning stage
  imports `schema` directly or through `review`, so a reverse edge would be a cycle. Import Linter
  skips the schema/planning overlap and checks the remaining edges.
- `uv run pytest`: 295 passed, 1 skipped; basedpyright, ruff F401, lint-imports, and actionlint are
  green.
