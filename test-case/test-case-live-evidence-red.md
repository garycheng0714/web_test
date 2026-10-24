---
id: live-evidence-red
base_url: https://automationexercise.com
---

# Live Evidence Red

## Case 1: 註冊 Step 1 / New User Signup!: Verify that a guest who submits a Name and an unregistered Email Address in the New User Signup! block is returned to the homepage with the Header showing "Logged in as OC QA"

```yaml
requirement_ids: [FR-LIVE-01]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- 訪客未登入，且網站 Header 顯示 `Signup / Login`
- 使用一個從未在 https://automationexercise.com 註冊過的 Email（unregistered）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Open https://automationexercise.com/login and locate the `New User Signup!` block | `/login` 頁面顯示 `New User Signup!` 區塊，且該區塊包含 Name 欄位、Email Address 欄位與 `Signup` 按鈕 |
| 2 | 在 `New User Signup!` 的 Name 欄位輸入 `OC QA` | Name 欄位顯示 `OC QA` |
| 3 | 在 Email Address 欄位輸入一個未註冊的 Email | Email Address 欄位顯示該輸入值 |
| 4 | 點擊 `Signup` 按鈕 | 使用者直接回到網站首頁，且不顯示任何 Account Information（Step 2）表單 |
| 5 | 檢視首頁 Header | Header 顯示 `Logged in as OC QA` |

### Notes

來源：FR-LIVE-01 AC1，逐字採用。此 PRD 為刻意錯誤的 fixture PRD：AC 描述的「直接登入 + Header 顯示 Logged in as OC QA」與 PRD 自身 Out of Scope（帳號資訊、建立帳號、登入）相互矛盾，預期在真實站台上失敗（實際會導向 Account Information 頁面）。矛盾與 Header 文字來源見 open_questions。

## Open Questions

- AC1 說點擊 `Signup` 後會「直接回到首頁並顯示已登入」，但同一份 PRD 的 Out of Scope 明確排除「帳號資訊、建立帳號、登入」。請問哪一個才是正確行為？註冊 Step 1 送出後，帳號是否已被視為建立完成？
- 送出 Step 1 後的正確落點頁面是什麼（首頁 `/`、Account Information 頁 `/signup`，或其它）？AC1 只寫「回到首頁」，未定義 URL。
- Header 的 `Logged in as OC QA` 是固定字串，還是會依 Step 1 輸入的 Name 動態組合（例如輸入 `Jane` 時應顯示 `Logged in as Jane`）？
- 若 Step 1 完成後真的會登入，原本給訪客的 `Signup / Login` 連結與 `Delete Account`、`Logout` 等 Header 項目應該如何變化？PRD 未定義登入後的 Header 內容。
- PRD 僅涵蓋「未註冊 Email」。若輸入已註冊的 Email，系統應顯示什麼訊息、停留在哪一頁？PRD 未定義。
- Name 或 Email Address 為空、或 Email 格式不合法時，系統的行為與錯誤訊息是什麼？PRD 未定義任何驗證規則。
- Email 唯一性比對是否區分大小寫、是否自動去除前後空白？PRD 未定義。
