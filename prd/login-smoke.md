# PRD：Automation Exercise 登入流程（smoke）

> **版本**：v0.1
> **URL**：http://automationexercise.com
> **說明**：極簡 PRD，用來驗證 plan 工作流（新增 `prd/*.md` 的 PR 被 merge 後觸發）。

## 1. 範圍

| In Scope | Out of Scope |
|---|---|
| 以 Email／Password 登入（成功與失敗） | 註冊、登出、刪除帳號、商品、購物車、結帳 |

## 2. 使用者角色

| 角色 | 狀態識別（Header） |
|---|---|
| 訪客（Guest） | 顯示 `Signup / Login` |
| 會員（LoggedIn） | 顯示 `Logged in as <name>` |

## 3. 功能需求

### FR-ACC-04 登入

- `/login` 頁面的 `Login to your account` 區塊含 Email Address、Password 欄位與 `Login` 按鈕。

**AC**

1. 輸入正確的 Email 與 Password，點 `Login` → Header 顯示 `Logged in as <name>`。
2. 輸入錯誤的 Email 或 Password，點 `Login` → 顯示錯誤訊息 `Your email or password is incorrect!`，並停留在 `/login`。

## 4. 訊息文案清單（Verbatim）

| 情境 | 文字內容（DOM text） |
|---|---|
| 登入區標題 | `Login to your account` |
| 登入狀態 | `Logged in as <name>` |
| 登入失敗 | `Your email or password is incorrect!` |

## 5. 假設與待確認

| # | 項目 | 說明 |
|---|---|---|
| 1 | 既存帳號來源 | 未定義；登入成功案例需要一個既存帳號，本 PRD 不描述其建立方式 |
| 2 | 必填與格式驗證 | 未涵蓋空值／格式錯誤的訊息 |
