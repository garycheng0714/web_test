# PRD：Automation Exercise 註冊 Step 1（live evidence — deliberate red）

> **版本**：v0.1
> **URL**：https://automationexercise.com
> **說明**：**刻意錯誤的 fixture PRD**，用來製造 red automation run 並驗證
> `.scratch/agent-in-ci/issues/07-red-run-evidence.md` 的 evidence 路徑與 17 的紅燈行為。
> 內容與 `prd/live-evidence.md` 相同，但 AC 故意描述不會發生的結果；用完即刪。

## 1. 範圍

| In Scope | Out of Scope |
|---|---|
| 以 Name + 未註冊 Email 送出 `New User Signup!` | 帳號資訊、建立帳號、登入、登出、刪除帳號、商品、購物車、結帳 |

## 2. 使用者角色

| 角色 | 狀態識別（Header） |
|---|---|
| 訪客（Guest） | 顯示 `Signup / Login` |

## 3. 功能需求

### FR-LIVE-01 註冊 Step 1 後直接登入（deliberately wrong）

- `/login` 的 `New User Signup!` 區塊含 Name、Email Address 欄位與 `Signup` 按鈕。
- **AC**
  1. 輸入 Name 與**未註冊**的 Email，點 `Signup` → 直接回到首頁且 Header 顯示
     `Logged in as OC QA`。
