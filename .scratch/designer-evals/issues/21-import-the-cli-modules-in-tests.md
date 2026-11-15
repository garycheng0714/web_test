# 21: Import the eval CLIs in their tests instead of loading them by path

**What to build:** Replace the two `_load()` helpers with ordinary imports of `evals.designer.report`, `export_labels` and `build_claims`.

**Blocked by:** Nothing.

**Status:** ready-for-agent

## Why

Two test files build their module under test from a file path:

- `tests/designer_evals/test_build_claims.py:13` loads `build_claims`;
- `tests/designer_evals/test_export_report.py:22` loads `export_labels` and `report`.

```python
spec = importlib.util.spec_from_file_location(f"designer_{name}", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
```

The loader is written twice, and the modules it returns are anonymous: `basedpyright` cannot check any attribute the tests then touch (`export_labels._label_rows`, `report.requirement_rows`, `report.render_report(design=…)`), so a rename that breaks a test's usage is only caught at run time. The module is also invisible to import-linter, which analyses source imports, not `spec_from_file_location`.

The helpers date from when `evals/designer/*.py` were scripts outside a package. That stopped being true when `evals` became a lint-imports root (ADR-0010): `from evals.designer import report` resolves now, and none of the three modules has import-time side effects (argparse lives in `main`).

## Tasks

- [ ] `from evals.designer import build_claims, export_labels, report` in the two test files; delete both `_load()` helpers and the `importlib.util` imports.
- [ ] Keep the tests' bodies unchanged apart from the module references (`build_claims.build_rows(...)` still reads the same).
- [ ] Confirm `uv run pytest tests/designer_evals` is green, then `uv run --group eval basedpyright` reports no new errors in `tests/designer_evals`.
- [ ] Check the two files' imports are sorted by ruff.

## Out of scope

- Merging `test_export_report.py` with `test_build_claims.py`.
- Any behaviour change in the three CLIs.

## Risks

- `export_labels` imports `designer_eval.phoenix` at module level; that module imports only the standard library and two package modules, so the default (non-`--group eval`) test environment still works. If that ever changes, this ticket's plain import would make the whole test module fail at collection instead of at one test — a louder failure, which is acceptable.
