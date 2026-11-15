# 22: Put the tests under `basedpyright`

**What to build:** Add `tests` to `[tool.basedpyright] include` and clear the errors it surfaces, starting with `tests/designer_evals`.

**Blocked by:** Nothing. Ticket 21 replaced the eval tests' `importlib` loaders, which is what made their usage of the CLIs visible to a type checker.

**Status:** needs-triage

## Why

`pyproject.toml` type-checks `web_test` and `evals/designer` only:

```toml
include = ["web_test", "evals/designer"]
```

`uv run --group eval basedpyright tests` reports **23 errors** that CI never sees. They fall into four groups:

| group | errors | example |
| --- | --- | --- |
| `tests/automation` | 12 | `None` passed where `ToolContext` is expected; `SimpleNamespace` standing in for a typed object |
| `tests/designer_evals` | 8 | `created_at="2026-11-13T00:00:00Z"` where the model declares `datetime`; `target_kind="claim"` where it declares `UnitKind` |
| `tests/publishing` | 1 | `total_seconds` on a value typed `None` |
| `tests/test_model.py` | 2 | `model_name` on a value typed `str` |

The eval group matters most: it is where the models gained their types in the last few commits, and the tests that construct them were never checked, so pydantic's runtime coercion hides the mismatch. A renamed field would still pass, because the tests pass strings or literals that only validate at run time.

The rest are mocks and fakes standing in for real types; fixing them may need `cast` or tighter fakes, and some may deserve `# pyright: ignore` with a reason.

## Tasks

- [ ] Add `tests/designer_evals` to `include` first; fix its 8 errors (they are small: pass `datetime(...)`, use `UnitKind.CLAIM`, type the `kind` parameter as the literal).
- [ ] Then add the rest of `tests` and work through the 15 remaining errors group by group.
- [ ] `uv run --group eval basedpyright` clean; `uv run pytest` unchanged.

## Out of scope

- Changing production types to accommodate a test's fake. If a fake needs a `cast`, the fake is what changes.
- Adding `tests` to import-linter. It analyses package imports, and tests are not a root package.

## Risks

- Turning on a stricter gate can surface a long tail in mock-heavy tests; if it does, land the eval group first and leave the rest to a follow-up ticket rather than weakening the setting.
- `typeCheckingMode` is `standard`, not `strict`; do not raise it in this ticket.
