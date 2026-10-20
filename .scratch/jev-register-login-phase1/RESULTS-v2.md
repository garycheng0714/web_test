# Phase 1 v2 實驗結果：修正 G2 與 B4 問題

日期：2026-10-20  
Provider：TypeSafe（`jev-1.13.0`）  
Request：`.scratch/jev-register-login-phase1/artifacts/request-v2.json`  
Response：`.scratch/jev-register-login-phase1/artifacts/response-v2.json`

## 這次改了什麼

1. G2 的 step 1、step 2 expected result 收斂成「表單顯示哪些欄位」，不再要求「輸入值被保留」这种 AC 沒明說的行為。
2. AC 對齊問題改成「PRD requirement text and acceptance criteria」，並明說 setup step 是允許的。
3. 新增每步的 `reachable` 問題：在目前 preconditions 與前序 steps 下，這一步是否可執行。

## 成本

| 指標 | 值 |
|---|---:|
| Input tokens | 11,805 |
| Output tokens | 1,285 |
| Elapsed | 0.437 s |
| Questions | 57 |
| Needs review | 7 |

## Good cases

| Case | AC 對齊 | 最低 step 分數 | 結果 |
|---|---:|---:|---|
| G1 | 0.94 | 0.92（observable） | 全部 ≥ 0.8 |
| G2 | 0.85 | 0.89（reachable / observable） | 全部 ≥ 0.8 |

G2 的 flag 消失了。上一版的 0.71 主要來自 expected result 超出 AC；收斂後變成 0.85。

## Bad cases

| Case | 目標問題 | 分數 | 結果 |
|---|---|---:|---|
| B1 不存在的控件 | `step_B1_1_reasonable` | 0.05 | 抓到 |
| B2 模糊 expected result | `step_B2_3_observable` | 0.06 | 抓到 |
| B3 與 AC 矛盾 | `ac_B3` | 0.03 | 抓到 |
| B4 跳過必要 step | `step_B4_1_reachable` | 0.80 | **還是沒抓到** |

B4 的其他訊號：

- `ac_B4` = 0.63（needs review）
- `step_B4_2_reachable` = 0.73（needs review）
- `step_B4_1_reasonable` = 0.89（selected true）

## 為什麼 B4 還是沒抓到

`reachable` 問的是「這一步能不能執行」。Jev 的答案是「可以」：`Create Account` 按鈕真的存在，使用者也真的在 `Enter Account Information` 頁面。它沒有把「必填欄位還沒填」視為不可執行，因為按鈕本身是可點的。

要抓 B4，問題需要問**完整性**，而不是可達性，例如：

> Does this step include every action required to produce its expected result, including required data entry?

這樣 Jev 才會注意到「Click Create Account」少了填欄位這一段。

## 對 kill criteria

| 條件 | 結果 |
|---|---|
| Bad 至少抓到 3/4 | 3/4（B1、B2、B3） |
| Good 不誤 flag | 通過（G1、G2 全部 ≥ 0.8） |
| 三組都有辨識力 | AC 對齊：有；Observable：有；Step 合理：B1 有、B4 沒有 |

## 目前的結論

- **AC 對齊**：可用。
- **Expected result 可觀察性**：可用。
- **Step 合理性**：對「不存在的控件」有效；對「跳過必要資料輸入」無效。
- G2 的修正證明上一版的 flag 是 artifact 問題，不是 Jev 的誤判。

下一步只剩一個小實驗：把 B4 的問題改成「完整性」，再跑一次。若 B4 被抓到，step 合理性也可以保留；若還是沒有，就把 step 合理性降級成 advisory，不單獨依賴。
