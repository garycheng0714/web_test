# 稀疏 PRD 實驗：`prd/login-smoke.md`

日期：2026-10-20  
Provider：TypeSafe（`jev-1.13.0`）  
目的：測試「PRD 完整度」是不是關鍵，以及 Jev 在稀疏 PRD 上能否把關。

## 三個 variants

| Variant | 內容 | Request |
|---|---|---|
| S1 | 稀疏 PRD + 原本較豐富的 login cases | `artifacts/request-login-smoke.json` |
| S2 | 稀疏 PRD + 移除超額細節，但保留「欄位顯示輸入值」 | `artifacts/request-login-smoke-aligned.json` |
| S3 | 稀疏 PRD + 只断言 PRD 明說的結果 | `artifacts/request-login-smoke-minimal.json` |

## 成本

| Variant | Input tokens | Output tokens | Elapsed | Needs review |
|---|---:|---:|---:|---:|
| S1 | 7,844 | 1,192 | 0.429 s | 24 / 54 |
| S2 | 7,798 | 1,192 | 0.364 s | 25 / 54 |
| S3 | 7,813 | 1,192 | 0.374 s | 19 / 54 |

## Good cases

| Variant | G1 AC | G2 AC | G1 最低分 | G2 最低分 | 結果 |
|---|---:|---:|---:|---:|---|
| S1 | 0.18 | 0.47 | 0.52 | 0.61 | 大量誤 flag |
| S2 | 0.67 | 0.70 | 0.70 | 0.68 | 仍被 flag |
| S3 | 0.94 | 0.82 | 0.91 | 0.82 | 全部 ≥ 0.8 |

## Bad cases（S3）

| Case | 目標問題 | 分數 | 結果 |
|---|---|---:|---|
| B1 不存在的控件 | `step_B1_1_reasonable` | 0.07 | 抓到 |
| B2 模糊 expected result | `step_B2_2_observable` | 0.06 | 抓到 |
| B3 與 AC 矛盾 | `ac_B3` | 0.02 | 抓到 |
| B4 跳過必要資料輸入 | `step_B4_1_complete` | 0.07 | 抓到 |

## 為什麼 S1、S2 會失敗

不是 Jev 在稀疏 PRD 上完全失效，而是 **good cases 超出了稀疏 PRD 的範圍**。

`prd/login-smoke.md` 只說：

- `/login` 的 `Login to your account` 區塊有 Email、Password、Login。
- 正確登入 → Header `Logged in as <name>`。
- 錯誤登入 → `Your email or password is incorrect!`，停留在 `/login`。

它沒有說：

- Header 有 `Logout`、`Delete Account`
- `New User Signup!` 仍可見
- Header 顯示 `Signup / Login`
- 輸入值會顯示在欄位裡

S1 的 good cases 來自 `register-login.md`，包含上述細節，所以 Jev 正確地把它們判為「超出 PRD」。S2 移除了部分細節，但仍保留「欄位顯示輸入值」，所以還是被 flag。

S3 只断言 PRD 明說的結果，good cases 才全部通過。

## 結論

1. **稀疏 PRD 可以用**，但 test case 只能断言 PRD 明說的行為。
2. **Jev 會把超出 PRD 的 expected result 判成 unsupported**，即使它在真實 UI 上可能正確。
3. 因此，真正的關鍵不是「PRD 很長」或「有截圖」，而是 **PRD 的 evidence 範圍與 test case 的断言範圍是否一致**。
4. 對 `register-login.md` 這種完整 PRD，Jev 可以驗證較豐富的 case；對 `login-smoke.md`，Jev 只能驗證最小 case。
5. 這其實是想要的行為：test case 不應該断言 PRD 沒說的行為。Jev 在這裡扮演 scope checker。

## 對「要不要走截圖」的意義

- 如果 PRD 已經精確到你想驗證的程度，截圖不是必要。
- 如果 PRD 很稀疏，但你想驗證更豐富的 UI 行為，就必須把那些行為寫進 PRD，或提供截圖/描述作為 evidence。
- Jev 不會替你發明 evidence；它只會檢查 case 是否被 supply 的 evidence 支持。

## 產物

- `artifacts/request-login-smoke.json` / `artifacts/response-login-smoke.json`
- `artifacts/request-login-smoke-aligned.json` / `artifacts/response-login-smoke-aligned.json`
- `artifacts/request-login-smoke-minimal.json` / `artifacts/response-login-smoke-minimal.json`
- `scripts/build_login_smoke.py` / `scripts/build_login_smoke_aligned.py` / `scripts/build_login_smoke_minimal.py`
