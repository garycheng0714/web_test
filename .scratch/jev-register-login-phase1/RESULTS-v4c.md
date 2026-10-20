# Phase 1 v4c 實驗結果：移除附錄 A

日期：2026-10-20  
Provider：TypeSafe（`jev-1.13.0`）  
Request：`.scratch/jev-register-login-phase1/artifacts/request-v4c.json`  
Response：`.scratch/jev-register-login-phase1/artifacts/response-v4c.json`

## 這次改了什麼

- 從 `prd_text` 移除「附錄 A：截圖」整段表格。
- 保留附錄 B、§3、§4、§6、§8。
- 沒有 `screen_descriptions`（與 v4b 相同）。
- 其餘 cases、57 題、review rules 不變。

## 成本

| 指標 | 值 |
|---|---:|
| Input tokens | 11,321 |
| Output tokens | 1,281 |
| Elapsed | 0.445 s |
| Questions | 57 |
| Needs review | 7 |

## 結果

| 檢查 | v4b（有附錄 A） | v4c（無附錄 A） |
|---|---:|---:|
| G1 AC 對齊 | 0.93 | 0.94 |
| G1 最低分 | 0.90 | 0.90 |
| G2 AC 對齊 | 0.87 | 0.88 |
| G2 最低分 | 0.87 | 0.88 |
| B1 `step_reasonable` | 0.05 | 0.05 |
| B2 `step_observable` | 0.06 | 0.06 |
| B3 `ac_alignment` | 0.03 | 0.03 |
| B4 `step_complete` | 0.13 | 0.15 |

- Bad cases：4/4 全抓到。
- Good cases：G1、G2 全部 ≥ 0.8，沒有被誤 flag。
- 與 v4b 的差異在噪音範圍內。

## 結論

對 `prd/register-login.md` 來說，**附錄 A 也是多餘的**。移除後 Jev 的判斷幾乎不變。

這表示真正提供訊號的是：

- §4 的 requirement 描述與 AC
- §6 的 verbatim messages
- §8 的 grounding details

不是附錄 A 的截圖索引，也不是 S1–S4 的結構化描述。

## 但這還不是最終答案

這份 PRD 仍然很完整。它只是沒有了附錄 A，仍然有 §4/§6/§8。所以 v4c 證明的是：

> 對這份 PRD，附錄 A 和 S1–S4 都不是必要條件。

它沒有證明：

- 稀疏 PRD 也有效。
- 只有截圖、沒有 §4/§6/§8 的 PRD 也有效。
- vision perception 可以取代文字。

## 下一個決定點

- **稀疏 PRD**：用 `prd/login-smoke.md` + login cases，測「PRD 完整度」是不是關鍵。
- **Phase 2**：用 vision model 從截圖產生描述，測 screenshot pipeline。
- **V4 的其他變體**：目前已不需要，因為附錄 A 和 S1–S4 都被證明是多餘的。
