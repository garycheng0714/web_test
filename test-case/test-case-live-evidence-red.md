---
id: live-evidence-red
base_url: https://automationexercise.com
---

# Live Evidence Red

## Case 1: Signup — New User Signup!（註冊 Step 1）: Verify that a guest who enters a Name and an unregistered Email in the `New User Signup!` block on `/login` and clicks `Signup` is taken directly to the homepage, where the header shows `Logged in as OC QA`.

```yaml
requirement_ids: [FR-LIVE-01]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- 使用者為訪客（未登入），網站 Header 顯示 `Signup / Login`。
- 備妥一組尚未註冊於本站的 Email（例如 `oc.qa.<timestamp>@example.com`）。

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 開啟 https://automationexercise.com/login | 顯示 `/login` 頁面，且 `New User Signup!` 區塊含 `Name` 與 `Email Address` 兩個輸入欄位及一顆 `Signup` 按鈕。 |
| 2 | 在 `Name` 欄位輸入 `OC QA`，在 `Email Address` 欄位輸入該組未註冊的 Email | 兩個欄位分別接受所輸入的值（`Name` = `OC QA`，`Email Address` = 該未註冊 Email）。 |
| 3 | 點擊 `Signup` 按鈕 | 直接回到網站首頁 https://automationexercise.com/（不應停留在 `/login`）。 |
| 4 | 檢視首頁 Header 的登入狀態文字 | Header 顯示 `Logged in as OC QA`。 |

### Notes

來源：FR-LIVE-01 AC1（含該需求對 `/login` 上 `New User Signup!` 區塊欄位與按鈕的描述；此 UI 檢查已併入步驟 1，不另立案例）。注意：本 PRD 自述為「刻意錯誤的 fixture PRD」，AC 描述的是實際系統不會發生的結果；本案例的預期結果仍依 PRD 原文撰寫，因此於真實系統上執行應會 red。AC 以 `OC QA` 作為 Name，故本案例沿用該值；若 Name 填入其他值時 Header 文案為何，PRD 未定義（見 open questions）。

## Open Questions

- FR-LIVE-01 AC1 描述送出 `Signup` 後「直接回到首頁並顯示已登入」，但範圍表把「帳號資訊、建立帳號」列為 Out of Scope，且本文件標題為「註冊 Step 1」。送出 `Signup` 後的正確產品行為應是：立即登入並回首頁，還是導向帳號資訊填寫（註冊 Step 2）？
- Header 文案 `Logged in as OC QA` 是固定字串，還是 `Logged in as <Name>` 樣板？若 Name 輸入其他值（例如 `Test User`），Header 應顯示什麼？
- 當輸入的 Email 已經註冊過時，`New User Signup!` 會顯示什麼訊息、或導向哪個頁面？
- `Name` 與 `Email Address` 是否為必填？任一欄位空白或僅輸入空白字元時，系統行為與提示訊息為何？
- `Name` 與 `Email` 是否有格式或長度限制？Email 前後空白是否會被 trim？Email 大小寫是否影響「未註冊」的判定？
- 登入狀態成立後，Header 是否仍顯示 `Signup / Login`？重新整理首頁或重新開啟網站後，此登入狀態是否保留？
