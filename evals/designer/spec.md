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
2. 這些 case 是否**真的**測到它宣稱的 requirement，且每個行為斷言都能從 PRD 推導出來，而不
   只是 `requirement_ids` 填了 ID？

## Failure modes

**Code-first（ticket 01／02）**

- requirement 沒被任何 case 覆蓋
- case 引用 PRD 沒有的 requirement ID
- case 的 `requirement_ids` 是空的
- 重複／near-duplicate case
- 格式問題（重用 `web_test/planning/review/structure.py`）

**Semantic labels（人類標註；ticket 03 judge 只預測 pass/fail）**

- `wrong_scenario_to_requirement`：case 的 steps 根本不在做它 claim 的 FR（scenario 是別的
  requirement，或是不存在的需求）。
- `undefined_behavior`：某個行為斷言無法用 PRD 判定——整份 PRD 沒寫（含第 11 章明列未定義
  者），或 assertion 本身太模糊（兩個 tester 會給不同答案，例如「商品與搜尋字相關」而 PRD
  沒給比對規則）。根因寫進 `claim_reason`，才分得出是 PRD 缺漏還是 assertion 模糊。
- `wrong_assertion_to_requirement`：某個行為斷言在 PRD 有依據，但推不出該 claim 的正文／AC，
  通常是驗了別的 FR 的行為。修法通常是換 assertion 或補 `requirement_ids`，不是刪步驟。
- `duplicated`：claim 的 FR 沒有自己的 scenario，只是搭在另一個 FR 的 case 上；同一組步驟
  同時服務兩個 FR，自動化會重複驗證且無法隔離失敗。修法是**拆 case**，不是刪斷言。

判定順序 `wrong_scenario` -> `undefined` -> `wrong_assertion` -> `duplicated`，先中先停；任一
成立，`claim_alignment` 即 `fail`。「斷言」只算會決定功能對錯的 `expected_result`；輸入被接受、
元件存在、欄位呈現這類前置／UI 細節不算；`no error`／`no blank state` 這類附加語也不算，
除非它本身就是該步要驗的結果。

「可推出」的界線：斷言要能從該 claim 的 FR 正文或 AC 推出。同一條已述規則套用在新輸入
（換一個關鍵字、換一組帳密再驗一次）算可推出；括號內的說明或理由不算斷言。

## Data

- PRDs：`prd/register-login.md`（FR-ACC-01~06）、`prd/login-smoke.md`、
  `prd/live-evidence.md`；必要時加 `.scratch/automationexercise/prd.md`。
- 每個 PRD 用 `design_test_cases` 跑一次；pin `WEB_TEST_DESIGN_MODEL`
  （預設 `openai-chat:deepseek-v4.1-flash`），記錄 model id 與 usage。
- 現有 `test-case/` 檔案只當 baseline／seed，不當 validation。
- 每次 run 存到 `evals/designer/runs/<run_id>/`：
  `design.json`、`run.json`、`units.json`、rendered markdown。
- Phoenix project：house run 用 `web-test-designer-eval`；old-skill probe 用
  `web-test-designer-eval-old-skill`，避免兩套 skill 的 trace 混在一起。每次 run 是一條
  designer trace，底下有 requirement 與 claim 的 `EVALUATOR` spans。

## Labels

- Claim level：`claim_alignment` = `pass` / `fail`（CATEGORICAL，`pass=1.0`、`fail=0.0`），
  每個 claim span（requirement × case）一筆。這是 judge 的目標與 coverage 的來源。
- `claim_failure_mode`：`wrong_scenario_to_requirement` / `undefined_behavior` /
  `wrong_assertion_to_requirement` / `duplicated`（CATEGORICAL，無 score，optimization
  direction `NONE`）；只在 `claim_alignment = fail` 時填。Phoenix UI 無法清空已選的值，所以
  `export_labels.py` 會丟掉非 fail claim 上的 mode。
- `claim_reason`：自由文字（FREEFORM）；fail 的 claim 記錄根因，pass 的 claim 也可以當註記
  （例如「teardown 待 ticket 29」）。
- Grounding 範圍是整份 PRD：§3 資訊架構、§6 文案、§7 資料模型都算「有描述」。
- Missing requirement：`requirement_covered` = `not_covered`，記在 requirement span。
- Code annotation：`case_duplicate`；MSG/ROLE 與未知 `FR-*` 列 report，不建 claim。
- 人類標註在 Phoenix UI 進行；`labels.jsonl` 是 metrics 的 source of truth。它是 long
  format：一個 claim 最多三列，per-claim 統計前要先 pivot。
- 現在只有一位 annotator；identifier 先預留 annotator，之後可加第二人。
- 每次 export 產生一份 snapshot，避免 Phoenix annotation 變動讓舊報告不可重現。

## Evaluators

- Code first：coverage、invented IDs、empty IDs、duplicates、structure。
- Semantic judge（ticket 03）：**整份 PRD + case**（`undefined_behavior` 需要整份 PRD 才知
  有沒有寫；`wrong_assertion_to_requirement` 需要該 FR 的正文／AC），binary Pass/Fail，
  critique 要引用缺少或錯置的 step／assertion。模型由 `WEB_TEST_JUDGE_MODEL` 指定（預設
  `openai-chat:kimi-k2.7-code`，與 designer 不同家族）；輸入不含人類標籤；輸出 JSONL + report
  到 `evals/designer/judge/runs/`。
- 一個 judge 只判一個準則：case 的每個行為斷言都在 PRD 有依據，且驗的是它宣稱的 FR。
  `duplicated` 由 CODE 的 `case_duplicate` 判，不進 judge；per-mode 只用來診斷。
- judge 預設只跑 single-FR case。multi-FR case 是 ticket 30 之前的歷史形狀，只在使用
  `--include-multi-fr` 時納入。
- 目前只有一份帶負例的 PRD，judge 只能做 dev（claim-level）；by-PRD split 等更多 PRD。
- `claim_failure_mode`／`claim_reason` 是人類分析欄位，不是 judge 的輸出，也不進 TPR/TNR。
- **不要用 Jev verifier 當 ground truth**：它同時是 gate，會循環。人類標籤才是 ground truth。

## Validation

- Coverage rate + Wilson 95% CI；per PRD。報兩個數字：`tested`（至少有一個 claim）與
  `clean`（至少有一個 pass claim）。
- `clean`：requirement 有任一 claim pass 即 `covered`；全部 claim fail 即 `not_clean`；
  沒有 claim 即 `missing`。`clean` 比 `tested` 嚴：一張 case 多驗一個斷言，就會讓它的
  requirement 不再是 clean。
- 比較 claimed coverage 與 human `claim_alignment`，報告 false tags。
- Semantic judge：兩個比例分開報，名稱自帶 positive class。
  `fail_recall` = P(judge fail | human fail)，`pass_specificity` = P(judge pass | human pass)；
  這是 `validate-evaluator` 的 TNR 與 TPR，讀 skill 時要換算。各附 Wilson 95% CI。
  split **by PRD**，避免同一個 PRD 的 cases 同時進 dev 與 test；只有一份 PRD 時報告標
  `dev only`。
- 每個比例同時報分母（confusion 計數）。某一類在標籤裡沒有樣本時報 `n/a`，不要報 0。
- 同一 prompt 至少跑 3 次再比較版本；run 之間的差距是雜訊下限，差距小於它就沒有結論。
- 報告取三次多數的 verdict。temperature 0 實測無法消除變異（2026-11-03），不要再試一次。
- 依 `claim_failure_mode` 分組計數，分母是已標的 claim（不是 failure_mode 的列數）。
  `undefined_behavior` 比例高時，先分清是 PRD 缺漏還是 skill 過度外推，再決定補 PRD 或調 skill。
- 樣本小時 report-only，不宣稱統計顯著。

## Integration

- 第一版只做 report-only，不改 `plan.py`、不改 `verify-test-case`。
- 工作檔案放 `evals/designer/`；驗證後再考慮 productionize 成
  `web_test/planning/eval/`。
- Phoenix 只在本機跑；late child `EVALUATOR` spans 已驗證可掛回原 designer trace。
- Phoenix/eval 工具在 `eval` dependency group；用 `uv run --group eval` 執行，版本由
  `uv.lock` 固定。
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
- Claim-centric 會讓 many-to-many 產生多個 claim spans；labels 必須用 claim id join。
- Missing requirement 只有一個 requirement span；不要用它取代 claim 標註。
- 每次 designer run 有模型成本。
- 不要用 Jev verifier 當 evaluator，否則量到的是 gate 的自己。
- `wrong_scenario_to_requirement` 在 automationexercise PRD 只有 3 例（2 例來自同一張
  case）；這一類的 TPR 不可用，需要其他 PRD 或合成負例。
- Label 同時量 alignment 與 grounding；只看總 fail 率會把兩者混在一起，必須按 mode 分開看。
- `clean` coverage 會把「有測到但多驗一步」的 requirement 算成 not_clean；解讀時要跟 `tested`
  一起看，否則會誤以為 designer 漏了需求。
- Judge 的 default 是浮動 alias（`kimi-k2.7-code`），provider 更新會讓舊數字漂；要比較版本時
  先固定 snapshot。
- 標籤的容差（teardown 不算 assertion、`e.g.` 不算）仍是情境判斷，換 PRD 可能漂。

## Ticket map

- [01](issues/01-eval-trace-and-units.md) — eval trace 與 claim／missing requirement 單位（unblocked）
- [02](issues/02-labels-and-coverage-report.md) — labels export 與 coverage report（blocked by 01）
- [03](issues/03-semantic-case-quality-judge.md) — semantic judge（blocked by 02）
- [04](issues/04-phoenix-experiments.md) — Phoenix experiments 比較多次 run（blocked by 01；02 可選）
- 05 — report-only CI：deferred，暫不開票

## Decisions

- 工作目錄：`evals/designer/`
- Ticket status：`needs-triage`
- `OPENCODE_API_KEY` 可用
- Phoenix 是人類標註 UI；`labels.jsonl` 是 metrics 的 source of truth
- Phoenix project：`web-test-designer-eval`
- Late child spans 驗證成功（2026-10-29），可直接掛回 designer trace
- CI 先不做；ticket 05 deferred
- ID policy：PRD heading 的 `FR-*` 是 authoritative；`FR-*-ACn` normalize 到 parent；
  `MSG-*`／`ROLE-*` 等非 PRD ID 仍算 invented
- Claim-centric：每個 requirement 一個 parent span；每個 case × valid FR 一個 claim span；missing requirement 另開 span
- Case ID：`case-{index}-{test_type}`，例如 `case-1-ui`、`case-6-data-persistence`
- 非 requirement 或未知 ID 不建 claim，只在 report 列出；multi-FR case 建 claims 並標 finding
- Label 三欄：`claim_alignment`、`claim_failure_mode`、`claim_reason`；mode 只在 fail 時填，
  reason 也可以當 pass 的註記
- Grounding 以整份 PRD 為準；failure mode 優先序 `wrong_scenario` -> `undefined` ->
  `wrong_assertion`
- Coverage 報 `tested`（有 claim）與 `clean`（有 pass claim）兩個數字
- 只把會決定功能對錯的 `expected_result` 當行為斷言；`no error`／`no blank state` 這類附加語不算
- Judge 目標維持 `claim_alignment`；`claim_failure_mode` 不進 TPR/TNR
- Old-skill probe 用獨立 project `web-test-designer-eval-old-skill`
- `labeling-worksheet.md` 是提案 artifact，不是 ground truth；由 run 產生、供人類在 UI 套用
- 一個 FR 一個 scenario：多 FR case 的次要 claim 若沒有獨立 scenario，標 `duplicated`
- 匯出時 `claim_failure_mode` 只保留在 fail claim 上；`claim_reason` 可保留在 pass 當註記
- Judge 判準收成一個：斷言在 PRD 有依據，且驗的是宣稱的 FR；`duplicated` 移到 CODE
- 斷言要能從 FR 正文／AC 推出；重複已述規則於新輸入、括號內的說明不算斷言
- Judge 預設只跑 single-FR；multi-FR 需要 `--include-multi-fr`
- Judge 比例叫 `fail_recall` / `pass_specificity`，不再用 TPR／TNR（兩套慣例方向相反）
- 第一版不改 production gate
