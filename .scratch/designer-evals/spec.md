# Designer evals

## Context

`web_test` 的 designer 讀 PRD，產生 `DesignOutput`（cases + open_questions），再 render 成
`test-case/<prd-stem>.md`。目前 designer 沒有直接 eval：它的輸出只經過人工 Gate 與 Jev
verifier（`verify-test-case`）間接把關。

這使得「PRD 需求有沒有被 cover」「宣稱的 `requirement_ids` 是否真的被測到」沒有獨立量測。
本 feature 建一個 designer eval：用 code evaluator 做 coverage/traceability，再加一個
semantic judge。Phoenix 只當 trace 與人類標註的review layer；metrics 仍由本機 Python 從
`labels.jsonl` 計算。第一版 report-only，不改 production gate。

## Goal

回答兩個問題：

1. 對一份 PRD，designer 是否為每個 requirement 產生至少一個 case？
2. 這些 case 是否**真的**測到它宣稱的 requirement，而不只是 `requirement_ids` 填了 ID？

## Failure modes

**Code-first（ticket 01／02）**

- requirement 沒被任何 case 覆蓋
- case 引用 PRD 沒有的 requirement ID
- case 的 `requirement_ids` 是空的
- 重複／near-duplicate case
- 格式問題（重用 `web_test/planning/review/structure.py`）

**Semantic judge（ticket 03）**

- case 沒有真的測到它宣稱的 requirement（AC alignment）
- 其他候選（expected result 不可觀察、step 引用 PRD 沒有的 control）留到後續 ticket

## Data

- PRDs：`prd/register-login.md`（FR-ACC-01~06）、`prd/login-smoke.md`、
  `prd/live-evidence.md`；必要時加 `.scratch/automationexercise/prd.md`。
- 每個 PRD 用 `design_test_cases` 跑一次；pin `WEB_TEST_DESIGN_MODEL`
  （預設 `openai-chat:deepseek-v4.1-flash`），記錄 model id 與 usage。
- 現有 `test-case/` 檔案只當 baseline／seed，不當 validation。
- 每次 run 存到 `.scratch/designer-evals/runs/<run_id>/`：
  `design.json`、`run.json`、`units.json`、rendered markdown。
- Phoenix project：`web-test-designer-eval`。每次 run 是一條 designer trace，底下有
  requirement 與 case 的 `EVALUATOR` spans。

## Labels

- Requirement level：`covered` / `not_covered`，記在被 cover 的 requirement span。
- Case level：`pass` / `fail`，記在 case span。
- Code annotation：`requirement_claimed`、`case_requirement_ids`、`case_duplicate`。
- 人類標註在 Phoenix UI 進行；`labels.jsonl` 是 metrics 的 source of truth。
- 現在只有一位 annotator；identifier 先預留 annotator，之後可加第二人。
- 每次 export 產生一份 snapshot，避免 Phoenix annotation 變動讓舊報告不可重現。

## Evaluators

- Code first：coverage、invented IDs、empty IDs、duplicates、structure。
- Semantic judge（ticket 03）：PRD requirement 文字 + case，binary Pass/Fail，critique 要引用
  缺少的 step／assertion；結果以 `LLM` annotation 或 JSONL 保存。
- **不要用 Jev verifier 當 ground truth**：它同時是 gate，會循環。人類標籤才是 ground truth。

## Validation

- Coverage rate + Wilson 95% CI；per PRD。
- 比較 `requirement_ids` 的 claimed coverage 與 human `covered`，報告 false tags。
- Semantic judge：TPR/TNR + CI；split **by PRD**，避免同一個 PRD 的 cases 同時進 dev 與 test。
- 樣本小時 report-only，不宣稱統計顯著。

## Integration

- 第一版只做 report-only，不改 `plan.py`、不改 `verify-test-case`。
- 工作檔案放 `.scratch/designer-evals/`；驗證後再考慮 productionize 成
  `web_test/planning/eval/`。
- Phoenix 只在本機跑；late child `EVALUATOR` spans 已驗證可掛回原 designer trace。
- CI 先不做；ticket 05 保留給未來的 report-only CI，目前不開票。
- 遵守 import contracts；eval 是 composition root，不讓 schema 反向依賴它。

## Non-goals

- 改 designer prompt 或 model
- 取代人工 Gate
- automation eval（下一個 feature）
- production monitoring 或 blocking gate
- 現在的 report-only CI
- 現在的自訂 review UI（Phoenix UI 不夠用再開）

## Risks

- 只有 3–4 個 PRD，CI 會很寬。
- 單一 annotator；需要 delayed self-review 或第二人。
- `requirement_ids` 可以被亂填；human labels 才是 ground truth。
- Phoenix annotations 與 `labels.jsonl` 可能漂移；用 export snapshot 固定。
- Phoenix 的 annotation UI 是 span-centric；若 requirement/case 標註太難用，再考慮自訂 UI。
- 每次 designer run 有模型成本。
- 不要用 Jev verifier 當 evaluator，否則量到的是 gate 的自己。

## Ticket map

- [01](issues/01-eval-trace-and-units.md) — eval trace 與 requirement／case 單位（unblocked）
- [02](issues/02-labels-and-coverage-report.md) — labels export 與 coverage report（blocked by 01）
- [03](issues/03-semantic-case-quality-judge.md) — semantic judge（blocked by 02）
- [04](issues/04-phoenix-experiments.md) — Phoenix experiments 比較多次 run（blocked by 01；02 可選）
- 05 — report-only CI：deferred，暫不開票

## Decisions

- 工作目錄：`.scratch/designer-evals/`
- Ticket status：`needs-triage`
- `OPENCODE_API_KEY` 可用
- Phoenix 是人類標註 UI；`labels.jsonl` 是 metrics 的 source of truth
- Phoenix project：`web-test-designer-eval`
- Late child spans 驗證成功（2026-10-29），可直接掛回 designer trace
- CI 先不做；ticket 05 deferred
- 第一版不改 production gate
