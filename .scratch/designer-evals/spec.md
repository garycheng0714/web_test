# Designer evals

## Context

`web_test` 的 designer 讀 PRD，產生 `DesignOutput`（cases + open_questions），再 render 成
`test-case/<prd-stem>.md`。目前 designer 沒有直接 eval：它的輸出只經過人工 Gate 與 Jev
verifier（`verify-test-case`）間接把關。

這使得「PRD 需求有沒有被 cover」「宣稱的 `requirement_ids` 是否真的被測到」沒有獨立量測。
本 feature 建一個 designer eval，先做 code-first 的 coverage/traceability，再加一個 semantic
judge；report-only，不急著改 production gate。

## Goal

回答兩個問題：

1. 對一份 PRD，designer 是否為每個 requirement 產生至少一個 case？
2. 這些 case 是否**真的**測到它宣稱的 requirement，而不只是 `requirement_ids` 填了 ID？

## Failure modes

**Phase 1（code-first）**

- requirement 沒被任何 case 覆蓋
- case 引用 PRD 沒有的 requirement ID
- case 的 `requirement_ids` 是空的
- 重複／near-duplicate case
- 格式問題（重用 `web_test/planning/review/structure.py`）

**Phase 2（semantic judge，一個 mode）**

- case 沒有真的測到它宣稱的 requirement（AC alignment）
- 其他候選（expected result 不可觀察、step 引用 PRD 沒有的 control）留到後續 ticket

## Data

- PRDs：`prd/register-login.md`（FR-ACC-01~06）、`prd/login-smoke.md`、
  `prd/live-evidence.md`；必要時加 `.scratch/automationexercise/prd.md`。
- 每個 PRD 用 `design_test_cases` 跑一次；pin `WEB_TEST_DESIGN_MODEL`
  （預設 `openai-chat:deepseek-v4.1-flash`），記錄 model id 與 usage。
- 現有 `test-case/` 檔案只當 baseline／seed，不當 validation。
- 每次 run 存 `DesignOutput` JSON、rendered markdown、model、usage 到
  `.scratch/designer-evals/traces/<prd>/`。

## Labels

- Requirement level：`covered` / `not covered`，並記錄被哪個 case 覆蓋。
- Case level：`tests its claimed requirement` / not。
- 人類標註；先做 delayed self-review，之後可加第二人。
- 存 `.scratch/designer-evals/labels.jsonl`。

## Evaluators

- Code first：coverage、invented IDs、empty IDs、duplicates、structure。
- Semantic judge（Phase 2）：PRD requirement 文字 + case，binary Pass/Fail，critique 要引用
  缺少的 step／assertion。
- **不要用 Jev verifier 當 ground truth**：它同時是 gate，會循環。人類標籤才是 ground truth。

## Validation

- Coverage rate + Wilson 95% CI；per PRD。
- 比較 `requirement_ids` 的 claimed coverage 與 human `covered`，報告 false tags。
- Phase 2：TPR/TNR + CI；split **by PRD**，避免同一個 PRD 的 cases 同時進 dev 與 test。
- 樣本小時 report-only，不宣稱統計顯著。

## Integration

- 第一版只做 report-only，不改 `plan.py`、不改 `verify-test-case`。
- 工作檔案放 `.scratch/designer-evals/`；驗證後再考慮 productionize 成
  `web_test/planning/eval/` 或 CI job。
- 遵守 import contracts；eval 是 composition root，不讓 schema 反向依賴它。

## Non-goals

- 改 designer prompt 或 model
- 取代人工 Gate
- automation eval（下一個 feature）
- production monitoring 或 blocking gate

## Risks

- 只有 3–4 個 PRD，CI 會很寬。
- 單一 annotator；需要 delayed self-review 或第二人。
- `requirement_ids` 可以被亂填；human labels 才是 ground truth。
- 每次 designer run 有模型成本。
- 不要用 Jev verifier 當 evaluator，否則量到的是 gate 的自己。

## Ticket map

- [01](issues/01-coverage-and-traceability-eval.md) — coverage & traceability eval（code-only）
- [02](issues/02-semantic-case-quality-judge.md) — semantic judge（blocked by 01）
- [03](issues/03-designer-eval-ci-report.md) — report-only CI（blocked by 01）

## Decisions

- 工作目錄：`.scratch/designer-evals/`
- Ticket status：`needs-triage`
- `OPENCODE_API_KEY` 可用
