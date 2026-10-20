# Phase 1 v3 實驗結果：B4 改用完整性問題

日期：2026-10-20  
Provider：TypeSafe（`jev-1.13.0`）  
Request：`.scratch/jev-register-login-phase1/artifacts/request-v3.json`  
Response：`.scratch/jev-register-login-phase1/artifacts/response-v3.json`

## 這次只改了 B4

- 移除 B4 的 `step_B4_1_reachable`、`step_B4_2_reachable`。
- 改成 `step_B4_1_complete`、`step_B4_2_complete`，問「這一步是否包含產生 expected result 所需的全部動作與輸入」。
- 其餘 cases、問題、state 與 v2 相同。

## 成本

| 指標 | 值 |
|---|---:|
| Input tokens | 11,797 |
| Output tokens | 1,281 |
| Elapsed | 0.489 s |
| Questions | 57 |
| Needs review | 6 |

## Good cases

| Case | 最低分數 | 結果 |
|---|---:|---|
| G1 | 0.94（AC） | 全部 ≥ 0.8 |
| G2 | 0.84（AC） | 全部 ≥ 0.8 |

## Bad cases

| Case | 目標問題 | 分數 | 結果 |
|---|---|---:|---|
| B1 不存在的控件 | `step_B1_1_reasonable` | 0.06 | 抓到 |
| B2 模糊 expected result | `step_B2_3_observable` | 0.06 | 抓到 |
| B3 與 AC 矛盾 | `ac_B3` | 0.03 | 抓到 |
| B4 跳過必要 step | `step_B4_1_complete` | 0.12 | **抓到** |

B4 的其他訊號：

- `step_B4_1_reasonable` = 0.87（selected true）
- `step_B4_1_observable` = 0.97
- `step_B4_2_complete` = 0.69（needs review）
- `ac_B4` = 0.59（needs review）

## 關鍵洞見

同一個 B4，換一個問題就從漏掉變成抓到：

- `reachable`（v2）：0.80，Jev 認為按鈕存在、頁面可達，所以 step 可執行。
- `complete`（v3）：0.12，Jev 發現這一步少了填必填欄位，无法產生 expected result。

所以 step 合理性不是一個單一問題。至少要分：

1. **合理**：控件與動作是否存在、是否符合流程。
2. **可達**：preconditions 與前序 steps 是否讓這一步可以執行。
3. **完整**：這一步是否包含產生 expected result 所需的全部動作與輸入。

## 對 kill criteria

| 條件 | 結果 |
|---|---|
| Bad 至少抓到 3/4 | 4/4，通過 |
| Good 不誤 flag | 通過（G1、G2 全部 ≥ 0.8） |
| 三組都有辨識力 | AC 對齊：有；Observable：有；Step 完整性：有 |

## 結論

Phase 1 通過。以人工 screen descriptions 為證據時，Jev 可以：

- AC 對齊
- Expected result 可觀察性
- Step 完整性（用 `complete` 問題，而不是 `reachable`）

下一個問題是 Phase 2：把人工描述換成 vision model 從截圖產生的描述，看這三個訊號是否仍然成立。這是真正要驗證的 screenshot pipeline。
