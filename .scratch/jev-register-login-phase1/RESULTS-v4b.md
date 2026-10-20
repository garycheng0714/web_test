# Phase 1 v4b 實驗結果：移除 S1–S4，只留 PRD 文字

日期：2026-10-20  
Provider：TypeSafe（`jev-1.13.0`）  
Request：`.scratch/jev-register-login-phase1/artifacts/request-v4b.json`  
Response：`.scratch/jev-register-login-phase1/artifacts/response-v4b.json`

## 這次改了什麼

- 移除 `state.screen_descriptions`（S1–S4）。
- 保留完整 `prd_text`，包含附錄 A、§3、§4、§6、§8。
- 保留同一組 57 題、6 個 cases、相同的 review rules。
- 問題文字從「screen descriptions」改成「PRD text」，因為這個 variant 沒有 screen descriptions。

## 成本

| 指標 | 值 |
|---|---:|
| Input tokens | 11,580 |
| Output tokens | 1,281 |
| Elapsed | 0.505 s |
| Questions | 57 |
| Needs review | 7 |

## 結果

| 檢查 | v3（有 S1–S4） | v4b（無 S1–S4） |
|---|---:|---:|
| G1 AC 對齊 | 0.94 | 0.93 |
| G1 最低分 | 0.94 | 0.90 |
| G2 AC 對齊 | 0.84 | 0.87 |
| G2 最低分 | 0.84 | 0.87 |
| B1 `step_reasonable` | 0.06 | 0.05 |
| B2 `step_observable` | 0.06 | 0.06 |
| B3 `ac_alignment` | 0.03 | 0.03 |
| B4 `step_complete` | 0.12 | 0.13 |

- Bad cases：4/4 全抓到。
- Good cases：G1、G2 全部 ≥ 0.8，沒有被誤 flag。
- 兩版的差異在噪音範圍內。

## 結論

對 `prd/register-login.md` 這份 PRD 來說，**S1–S4 是多餘的**。只給 Jev 完整的 PRD 文字，結果幾乎一樣。

這支持了先前的假設：這份 PRD 本身非常完整，§4 有欄位與 AC、§6 有 verbatim messages、§8 有 grounding details，所以 Jev 不需要額外的結構化描述。

但這還不是「PRD 完整度是關鍵」的證明，因為：

- 只測了一份 PRD。
- 這份 PRD 仍包含附錄 A、§3、§4、§6、§8。
- 沒有測稀疏 PRD（例如 `prd/login-smoke.md`）。
- 沒有測移除 §4/§6/§8 後的情況。

## 對 production 的意義

目前 `web_test/planning/review.py` 的 `ReviewState` 只有 `prd` 與 `cases`，正好對應 v4b。也就是說：

- 對這種完整的 PRD，Jev 可以直接接進現有 pipeline，不需要 S1–S4 或圖片。
- 需要新增的是問題集、報告區段、以及把 verdict 放進 PR body。
- 稀疏 PRD 是否也有效，仍然未知。

## 下一個決定點

- 要測「PRD 完整度」：用 `prd/login-smoke.md` + login cases 跑同一組問題。
- 要測「附錄 A 是否也有貢獻」：已跑 V4c，見 [`RESULTS-v4c.md`](RESULTS-v4c.md)；結果顯示附錄 A 也是多餘的。
- 要測「截圖是否能取代文字」：Phase 2（vision → Jev）。
