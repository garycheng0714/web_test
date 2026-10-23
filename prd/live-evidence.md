# PRD：Automation Exercise 註冊 Step 1（live evidence）

> **版本**：v0.1
> **URL**：https://automationexercise.com
> **說明**：極簡單一需求 PRD，讓單一 case 的 Test Case PR 能通過驗證並觸發 automation 的
> red-run evidence 路徑（`.scratch/agent-in-ci/issues/07-red-run-evidence.md`）。內容取自
> `prd/register-login.md` 的 FR-ACC-01。

## 1. 範圍

| In Scope | Out of Scope |
|---|---|
| 以 Name + 未註冊 Email 送出 `New User Signup!` | 帳號資訊、建立帳號、登入、登出、刪除帳號、商品、購物車、結帳 |

## 2. 使用者角色

| 角色 | 狀態識別（Header） |
|---|---|
| 訪客（Guest） | 顯示 `Signup / Login` |

## 3. 功能需求

### FR-ACC-01 註冊 Step 1：Name + Email

- `/login` 的 `New User Signup!` 區塊含 Name、Email Address 欄位與 `Signup` 按鈕。
- **AC**
  1. 輸入 Name 與**未註冊**的 Email，點 `Signup` → 進入 `Enter Account Information` 頁。

## 4. 訊息文案清單（Verbatim）

| 情境 | 文字內容（DOM text） |
|---|---|
| 註冊區標題 | `New User Signup!` |
| 按鈕 | `Signup` |
| 帳號資訊頁標題 | `Enter Account Information` |
