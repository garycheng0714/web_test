# Run eval 重構 review

日期：2026-11-02
範圍：`HEAD` 583044f 之後的未提交工作樹
固定點：`HEAD`
Spec 來源：使用者重構要求、`spec.md`、`issues/01`、`issues/02`

兩軸 review，分開記錄，不合併排序。

## 驗證基線

```text
uv run pytest tests/designer_evals -q    22 passed
uv run pytest -q                         328 passed, 5 deselected
uv run basedpyright                      0 errors
uv run ruff check                        All checks passed
uv run ruff format --check               108 files already formatted
uv run lint-imports                      5 kept, 0 broken
```

沒有發現行為 regression。

## Standards

### Hard

- `run_eval.py` 殘留未使用的 `pathlib.Path`，import block 也未排序。
  `ruff` 顯示 `F401`、`I001`、`PLR0915`、`UP017`。
  預設 `uv run ruff check` 不會抓到，因為 `pyproject.toml` 的 `include` 沒有 `.scratch/**`。
  這是新拆出的套件不在 repo 靜態檢查範圍內的直接證據。

### Judgement

- `artifacts.py` 的 `RunMetadata` 與 issue 01 Shape 的 `EvalRun` 名稱不一致。
  `RunMetadata` 還帶著 `design` 與 `units` payload，名稱容易誤導。
- 新增六個模組，ticket 沒有補 `AGENTS.md` 要求的六行 module plan。
- `phoenix.py` 的 `base` 參數與 `run_eval.main(argv)` 主要為測試或未使用，帶有 Speculative Generality。
- endpoint 邏輯仍有四份：`phoenix/spike.py`、`late_child_probe.py`、`spike_register.py`、`export_labels.py`。
  `export_labels.py` 的版本沒有 `/v1/traces` 正規化。
  `run_eval.py` 的 summary 也還硬寫 `http://127.0.0.1:6006`。
- `EvalUnit` 重複 `UnitSpec` 的四個欄位，`create_units` 再逐欄複製。
  若理由是 `asdict(unit)` 需要固定扁平 JSON，應註明。
- `annotations.py` 直接讀 `unit.attributes`，對 `EvalUnit` 的內部資料有 Feature Envy。
- `units.py` 同時承擔 duplicate detection 與 claim planning，是 Divergent Change。
- 測試的 `_case` / `Case.model_validate` dict 在 `test_annotations.py` 與 `test_artifacts.py` 重複。
- `tests/designer_evals/conftest.py` 的 `sys.path.insert` 是手動 hack。
  `pyproject.toml` 已有 `pythonpath`，可以加 `evals/designer` 取代。

## Spec

### 缺失或 partial

- `phoenix.py` 測試覆蓋不完整。
  `test_phoenix.py` 只測 `endpoint`、`base_url`、`sum_usage`。
  `create_provider`、`instrument_designer`、`create_client`、`find_agent_span`、`create_units`、`fetch_usage`、`log_code_annotations` 沒有測試。
  完成條件是「且有測試覆蓋」，目前只覆蓋純邏輯半邊。
- issue 01 Shape 要求 run/unit records 寫入 JSON 時是 Pydantic。
  `artifacts.py` 仍用 raw dict 與 `asdict`。
  HEAD 原本如此，重構保留未修。
- issue 01 Shape 明列 `EvalRun`，實作叫 `RunMetadata`。
  功能沒有缺，但名稱未對齊 shape。

### Scope creep

- 沒有實質新增功能。
- `UnitKind` StrEnum、`endpoint`/`base_url` 的 `base` 參數、`DEFAULT_ENDPOINT`、`main(argv)` 是行為不變的可測性小改。

### 實作可疑

- `designer_eval` 無法獨立匯入，測試靠 conftest 的 `sys.path.insert`。
  `__init__.py` 沒有匯出任何符號。
- `RunMetadata.prd` 存絕對 `Path`，但 `write_results` 只取 `.name`，型別沒有縮窄。

## 結論

- Standards：1 個 hard breach，9 個 judgement call。
  最嚴重的是新模組不在 lint／typecheck 閘門內。
- Spec：3 個缺失或 partial，2 個實作可疑。
  最嚴重的是 Phoenix adapter 幾乎沒有測試。

目前狀態：全部 finding 仍 open，尚未套用修正。

## 後續（2026-11-02）

- `evals/designer` 已納入 Ruff，pre-commit 的 `files` regex 同步更新。
- `evals/designer` 已納入 Basedpyright，`evals/designer/phoenix` 的 probes 排除。
- 14 個 Ruff finding 與 5 個 runtime type error 已修。
- Phoenix adapter 已補 fake-client／fake-tracer 測試：agent span 查詢、usage、units parent context、annotation payload。
- 真正連線 Phoenix 的 ingestion 與 annotation 寫入仍只由手動 smoke 驗證。
