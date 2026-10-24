# 19: Extend the import contracts to the full dependency graph

**What to build:** Ticket 12 added two contracts. Add the missing directions so the layering is
enforced, not just conventional. No production code change unless a contract exposes a real
violation.

Contracts to add:

- `web_test.publishing` is a leaf: it must not import `web_test.planning` or `web_test.automation`.
- `web_test.planning.schema` is a leaf: it must not import `web_test.planning.review`,
  `web_test.planning.verify`, `web_test.publishing`, or `web_test.automation` (extends the existing
  schema contract).
- `web_test.planning` does not import `web_test.automation` (replaces the narrower review-only
  contract).
- `web_test.planning.review` does not import `web_test.planning.verify`.
- `web_test.automation` does not import `web_test.planning.review` or `web_test.planning.verify`
  (only `web_test.planning.schema` is allowed).

**Shape:** only `[tool.importlinter]` contracts in `pyproject.toml`. Invariant: the baseline passes
with 0 broken; a failing contract is a real dependency to fix, not a reason to weaken the rule.

**Blocked by:** None.

**Status:** ready-for-agent

- [ ] The five directions above are enforced by `forbidden` contracts
- [ ] `uv run lint-imports` passes (record the file/dependency count)
- [ ] If any new contract fails, record the actual import in this ticket instead of relaxing it
- [ ] The `contracts` CI job needs no change and stays green
- [ ] `uv run pytest`, `uv run basedpyright`, `uv run ruff check --select F401`, and `actionlint` pass

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
