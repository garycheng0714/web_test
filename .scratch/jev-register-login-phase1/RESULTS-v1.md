# Phase 1 實驗結果：人工描述 + Jev

> 後續迭代見 [`RESULTS-v2.md`](RESULTS-v2.md)、[`RESULTS-v3.md`](RESULTS-v3.md)、[`RESULTS-v4b.md`](RESULTS-v4b.md)、[`RESULTS-v4c.md`](RESULTS-v4c.md) 與 [`RESULTS-login-smoke.md`](RESULTS-login-smoke.md)。

日期：2026-10-20  
Provider：TypeSafe（`jev-1.13.0`）  
Request：`.scratch/jev-register-login-phase1/artifacts/request-v1.json`  
Response：`.scratch/jev-register-login-phase1/artifacts/response-v1.json`  
State：`prd/register-login.md` + S1–S4 人工 screen descriptions + 6 個 cases（2 good、4 bad）  
Images：無（Phase 1 只用文字）

## 成本

| 指標 | 值 |
|---|---:|
| Input tokens | 9,833 |
| Output tokens | 894 |
| Elapsed | 0.485 s |
| Questions | 40 |
| Needs review | 6 |

## Good cases

| Case | AC 對齊 | Step 合理（最低） | Observable（最低） | 結果 |
|---|---:|---:|---:|---|
| G1（FR-ACC-01） | 0.90 | 0.96 | 0.94 | 全部 ≥ 0.8，通過 |
| G2（FR-ACC-02） | **0.71** | 0.95 | 0.92 | AC 對齊 needs review |

G2 的 AC 對齊被標為 needs review。這是本次唯一的 good-case flag。它可能是真的：G2 的 step 1 expected result 要求「selected title、password、date of birth、checkboxes 被保留；Email 仍顯示 Step 1 的值」，但 `prd/register-login.md` 的 FR-ACC-02 AC 只說「Create Account → Account Created」與「Continue → logged in」，沒有明說欄位保留。若以 AC 為標準，G2 的 expected result 比 AC 更細，Jev 的 flag 是合理的。

## Bad cases

| Case | 目標 | 實際 | 結果 |
|---|---|---|---|
| B1 不存在的控件 | `step_B1_1_reasonable` < 0.5 | 0.05 | 抓到 |
| B2 模糊 expected result | `step_B2_3_observable` < 0.5 | 0.07 | 抓到 |
| B3 與 AC 矛盾 | `ac_B3` < 0.5 | 0.03 | 抓到 |
| B4 跳過必要 step | `step_B4_1_reasonable` < 0.5 | 0.84 | **沒抓到** |

B4 的 AC 對齊是 0.51（needs review），但 targeted 的 step 合理性沒有被抓到。Jev 認為「Click Create Account」本身是合理的，因為按鈕真的存在；它沒有把「未填欄位」視為 step 不合理的理由。

## 其他觀察

- B1 的 `step_B1_1_observable` 是 0.47，代表 Jev 也發現 expected result 指到的欄位不在該畫面；這是額外訊號。
- B2 的 `step_B2_1_observable` 是 0.78，代表「The block is displayed」也被視為稍微模糊。
- B3 的 `step_B3_3_reasonable` 是 0.80，剛好壓線；Jev 沒有把「停留在 /login」視為 step 不合理，而是由 AC 對齊抓到。
- B4 是 step reasonableness 的弱點：它需要「這個 step 在目前 precondition 下是否可達」這種判斷，而不只是「控件是否存在」。

## 對 kill criteria 的結果

| 條件 | 結果 |
|---|---|
| Bad 至少抓到 3/4 | 3/4（B1、B2、B3）；B4 沒抓到，壓線通過 |
| Good 不誤 flag | G1 通過；G2 的 AC 對齊 0.71，未通過（除非把 G2 視為真實 finding） |
| 三組至少各有辨識力 | AC 對齊：有；Observable：有；Step 合理：只在 B1 有，B4 沒有 |

## 解讀

Jev 在人工描述下可以做：

- **AC 對齊**：強。B1、B2、B3 都低於 0.5；G1 是 0.90。
- **Expected result 可觀察性**：強。B2 的模糊結果是 0.07；好案例 ≥ 0.92。
- **Step 合理性**：部分。能抓到「不存在的控件」（B1），但抓不到「跳過必要前置步驟」（B4）。

G2 的 0.71 不是單純的 false positive。它指出 G2 的 expected result 比 PRD AC 更細，這是 artifact 層級的問題，不是 Jev 的誤判。

## 下一步選項

1. 把 B4 的問題改成「這個 step 在目前 precondition 下是否可達」，再跑一次，看 step 合理性是否補得起來。
2. 把 G2 的 step 1 expected result 收斂到 AC 有明說的行為，或把它標成「超出 AC 的 grounding 觀察」，再跑一次確認 Jev 的 flag 消失。
3. 接受目前結果：AC 對齊與 observability 可用，step 合理性只當 advisory，不單獨依賴。
4. 進入 Phase 2：用 vision model 把截圖轉成描述，再測 Jev 的判斷是否仍成立。
