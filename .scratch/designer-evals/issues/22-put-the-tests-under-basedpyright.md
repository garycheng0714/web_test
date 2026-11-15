# 22: Put the tests under `basedpyright`

**What to build:** Add `tests` to `[tool.basedpyright] include` and clear the errors it surfaces, starting with `tests/designer_evals`.

**Blocked by:** Nothing. Ticket 21 replaced the eval tests' `importlib` loaders, which is what made their usage of the CLIs visible to a type checker.

**Status:** needs-triage

## Why

`pyproject.toml` type-checks `web_test` and `evals/designer` only:

```toml
include = ["web_test", "evals/designer"]
```

`uv run --group eval basedpyright tests` reports **22 errors** that CI never sees. They fall into four groups:

| group | errors | example |
| --- | --- | --- |
| `tests/automation` | 11 | `None` passed where `ToolContext` is expected; `SimpleNamespace` standing in for a typed object |
| `tests/designer_evals` | 8 | `created_at="2026-11-13T00:00:00Z"` where the model declares `datetime`; `target_kind="claim"` where it declares `UnitKind` |
| `tests/publishing` | 1 | `total_seconds` on a value typed `None` |
| `tests/test_model.py` | 2 | `model_name` on a value typed `str` |

The eval group matters most: it is where the models gained their types in the last few commits, and the tests that construct them were never checked, so pydantic's runtime coercion hides the mismatch. A renamed field would still pass, because the tests pass strings or literals that only validate at run time.

The rest are mocks and fakes standing in for real types; fixing them may need `cast` or tighter fakes, and some may deserve `# pyright: ignore` with a reason.

## Tasks

- [x] Add `tests/designer_evals` to `include` first; fix its 8 errors (they are small: pass `datetime(...)`, use `UnitKind.CLAIM`, type the `kind` parameter as the literal).
- [x] Then add the rest of `tests` and work through the remaining errors group by group.
- [ ] `uv run --group eval basedpyright` clean; `uv run pytest` unchanged.

## Out of scope

- Changing production types to accommodate a test's fake. If a fake needs a `cast`, the fake is what changes.
- Adding `tests` to import-linter. It analyses package imports, and tests are not a root package.

## Risks

- Turning on a stricter gate can surface a long tail in mock-heavy tests; if it does, land the eval group first and leave the rest to a follow-up ticket rather than weakening the setting.
- `typeCheckingMode` is `standard`, not `strict`; do not raise it in this ticket.

## Result

`[tool.basedpyright] include` is `["web_test", "evals/designer", "tests"]`; the whole suite is in the
gate and reports **0 errors** (it reported 22 before any of this, and 14 after the eval group was
fixed).

`tests/designer_evals` (8 errors, done first):

- `created_at="2026-11-13T00:00:00Z"` → `datetime(2026, 11, 13, tzinfo=UTC)` in the two fixtures
  that build a `RunSummary`;
- `target_kind="claim"` → `UnitKind.CLAIM` in the three places that build an `AnnotationRow`;
- `_label(..., kind: str)` → `kind: Literal["HUMAN", "CODE"]`;
- `_FakeTracer.calls` / `start_as_current_span` annotated with `Context | None`, so
  `get_current_span(context)` type-checks instead of receiving `object`.

Six of those eight came from the model typing in tickets 12-16: the tests were never in the gate, so
pydantic's runtime coercion hid fields that had become `datetime` or an enum.

The remaining 14:

- `tests/automation/test_coding_agent.py` (3): three `agent.run(prompt)` calls on an
  `Agent[AutomationDeps, …]` now pass `deps=AutomationDeps()`. This was not only a type error: the
  runs had `deps=None`, and a tool reading `ctx.deps` would have raised `AttributeError`.
- `tests/automation/test_repair_guard.py` (8): a `_ctx()` helper casts a `SimpleNamespace` to
  `RunContext[AutomationDeps]` (the handlers read only `ctx.deps`), `call` and `tool_def` are real
  `ToolCallPart` / `ToolDefinition` objects instead of `None`, and the hook decorator's sync-or-async
  overloads are narrowed with one cast where `run_sync` needs a coroutine.
- `tests/publishing/test_github.py` (1): `completed_at.utcoffset()` may be `None`, so the assertion
  compares the offset to `timedelta(0)` instead of calling through it.
- `tests/test_model.py` (2): `resolve_model()` returns `Model | str`, so the tests narrow with
  `isinstance(model, OpenAIChatModel)` before reading `model_name`.

391 tests, ruff, 8 contracts and `basedpyright` all pass. The gate was proved live by planting a
type error in each of `tests/designer_evals` and `tests/automation`: both are reported.

## Comments

2026-11-15: the human chose the narrow group first, then asked for the remaining 14 in the same
session. Closing both phases under this ticket rather than opening a second one: the outcome is one
thing (the tests are in the gate), and the second phase only made the include list unconditional.
