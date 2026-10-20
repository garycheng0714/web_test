# Jev 品質檢查研究：AC 對齊、step 品質、expected result 可觀察性

日期：2026-10-19 至 2026-10-20  
研究問題：Jev 能不能對 test-case 產出做三種判斷，並且在 `plan` 階段作為 advisory review？

- AC 對齊
- Step 品質（合理、可達、完整）
- Expected result 可觀察性

## 方法

Jev（TypeSafe `jev-1.13.0`）是 text-only。所有 request 只包含：

- PRD 文字
- `DesignOutput` 的 cases 與 steps
- typed `Noul` 問題

沒有圖片、沒有 screen descriptions、沒有附錄 A parsing。這點很重要：後來的 v4b/v4c 證明，對 `prd/register-login.md` 而言，這些額外描述都不是必要條件。

實驗使用兩份 PRD：

- `prd/register-login.md`：完整、從 live walkthrough 反推，含 §4 欄位、§6 verbatim messages、§8 grounding details。
- `prd/login-smoke.md`：稀疏，只有 2 條 AC 與 3 條 verbatim messages。

## 時間線

| 版本 | 問題設計 | 結果 |
|---|---|---|
| v1 | per-case groundedness + 基本 step/observable | B4 漏掉；AC 對齊與 observability 有訊號 |
| v2 | 加 `reachable` | B4 仍漏掉（0.80）；reachable 被理解成「按鈕可按」 |
| v3 | B4 改成 `complete` | B4 抓到（0.12）；4/4 bad、2/2 good 通過 |
| v4b | 移除 S1–S4，只留完整 PRD 文字 | 結果幾乎不變 |
| v4c | 再移除附錄 A | 結果幾乎不變 |
| S1–S3 | 稀疏 PRD + login cases | 豐富 cases 被 flag；收斂到 PRD 明說的行為後全部通過 |

詳細數字在 [`RESULTS-v1.md`](../../.scratch/jev-register-login-phase1/RESULTS-v1.md) 到 [`RESULTS-v4c.md`](../../.scratch/jev-register-login-phase1/RESULTS-v4c.md)，以及 [`RESULTS-login-smoke.md`](../../.scratch/jev-register-login-phase1/RESULTS-login-smoke.md)。

## B4 的演進

B4 是「在 `Enter Account Information` 頁直接按 `Create Account`，沒有填必填欄位，期待 `Account Created!`」。

| 版本 | 問題 | Jev 分數 | 結果 |
|---|---|---:|---|
| v1 | `reasonable`：控件與動作是否存在 | 0.84 | 漏掉 |
| v2 | `reachable`：這一步能不能執行 | 0.80 | 漏掉 |
| v3 | `complete`：是否包含所有必要動作與輸入 | 0.12 | 抓到 |

原因：

- `reasonable` 只問控件是否存在；按鈕真的存在。
- `reachable` 只問動作能不能被嘗試；按鈕真的可按。
- `complete` 問這一步是否具備產生 expected result 的全部條件；缺少填欄位，所以不完整。

這是整個研究最重要的方法論發現：**verifier 漏掉 known-bad case 時，先檢查問題是否命名了那個失敗模式，再判斷 verifier 的能力。**

## 三個檢查

最終採用的 question set：

- `ac_{i}`：case 是否由 PRD requirement text 與 AC 支持。
- `step_{i}_{j}_reasonable`：step 的動作與目標是否存在、是否符合 PRD flow。
- `step_{i}_{j}_complete`：step 是否包含產生 expected result 所需的全部動作與輸入。
- `step_{i}_{j}_observable`：expected result 是否具體、可由 PRD text 或 verbatim messages 觀察。

沒有 `reachable`。v2 顯示它對 B4 沒有額外貢獻，而 `complete` 才是有效的問題。

## 關鍵結論

1. **Evidence 範圍要與 case 断言範圍一致。**
   - `register-login.md` 的 cases 可以断言較豐富的 UI 行為，因為 PRD 有那些細節。
   - `login-smoke.md` 的 cases 只能断言 PRD 明說的行為。超出範圍會被 Jev flag，即使它在真實 UI 上可能正確。

2. **對完整 PRD，截圖描述不是 Jev 的必要條件。**
   - v4b 移除 S1–S4，結果不變。
   - v4c 移除附錄 A，結果不變。
   - 訊號來自 PRD 的 requirement text、verbatim messages、grounding details。

3. **對稀疏 PRD，Jev 仍然可用，但只能做 scope checking。**
   - 稀疏 PRD + 最小 cases：good cases 全部 ≥ 0.8，4/4 bad 全抓到。
   - 稀疏 PRD + 豐富 cases：good cases 被大量 flag，因為它們断言了 PRD 沒說的行為。

4. **Jev 是 advisory。**
   - 它不擋 plan PR。
   - `run_review` 在 Jev 不可用時回傳 `None`，plan 照常進行。
   - 人類 Gate 仍然是最終決定。

## 實作

票 18：[`18-add-jev-quality-checks.md`](../../.scratch/prd-to-tests/issues/18-add-jev-quality-checks.md)

- `web_test/planning/review.py`：`ReviewStep`、`ac_{i}`、`step_*_{reasonable,complete,observable}`、`JEV_MODEL = "jev-1.13.0"`。
- `web_test/planning/review_report.py`：`AC alignment` 與合併的 `Step quality` 區段。
- Tests：`tests/planning/test_review.py`、`test_review_report.py`、`test_plan.py`。

驗證：

- `uv run pytest tests/planning`：34 passed
- `uv run pytest`：103 passed, 1 skipped
- Live review-only on `prd/login-smoke.md`：3 cases、8 steps；AC 3/3；step quality 8/8 reasonable、8/8 complete、7/8 observable；advisory only。

## 尚未處理

- PRD 完整度的定義與維護流程。
- Vision model 從截圖產生描述（Phase 2）。
- Coverage、dedup、requirement_ids 存在性、case body 結構。
- 大型 artifact 的 request batching。
- 以 Jev 作為 blocking gate。

## 相關檔案

- Experiment index：[`README.md`](../../.scratch/jev-register-login-phase1/README.md)
- 原始 request/response：`.scratch/jev-register-login-phase1/artifacts/`（本機保留，未進版控）
- 產生腳本：`.scratch/jev-register-login-phase1/scripts/`
- Pstack 研究：[`pstack.md`](pstack.md)
- 學習紀錄：[`0009-pstack-learning-priorities.md`](../learning-records/0009-pstack-learning-priorities.md)
