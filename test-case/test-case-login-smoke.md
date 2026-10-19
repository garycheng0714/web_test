---
id: login-smoke
base_url: https://automationexercise.com
---

# Login Smoke

## Case 1: 帳號 / 登入（Login）: Verify that a guest can log in with a valid email and password and that the header switches to the logged-in state.

```yaml
requirement_ids: [FR-ACC-04, FR-ACC-04/AC1]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- 使用者為訪客（未登入），Header 顯示 `Signup / Login`
- 系統中已存在一組可登入的帳號（Email 與對應 Password）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 前往 http://automationexercise.com/login 並確認 `Login to your account` 區塊內容 | 頁面載入 `/login`；`Login to your account` 區塊顯示 `Email Address` 欄位、`Password` 欄位與 `Login` 按鈕（文案與 §4 一致） |
| 2 | 在 `Email Address` 輸入該既存帳號的 Email，在 `Password` 輸入對應的密碼 | 兩個欄位接受輸入，內容顯示於欄位中（Password 依欄位預設顯示方式呈現） |
| 3 | 點擊 `Login` 按鈕 | Header 不再顯示 `Signup / Login`，改為顯示 `Logged in as <name>`，其中 `<name>` 為該帳號的名稱 |
| 4 | 確認頁面上未出現 `Your email or password is incorrect!` 訊息 | 登入成功時不顯示任何登入失敗訊息 |

### Notes

來源：FR-ACC-04 AC1、§3、§4。`Login to your account` 標題與欄位／按鈕存在性已折入步驟 1，不另立 UI 案例（避免與本案例重複）。既存帳號的建立方式 PRD §5#1 未定義，執行前需由環境提供。

## Case 2: 帳號 / 登入（Login）: Verify that logging in with an incorrect email or an incorrect password shows the failure message and keeps the user on the login page.

```yaml
requirement_ids: [FR-ACC-04, FR-ACC-04/AC2]
priority: High
test_type: Negative
```

**Severity:** Major

### Preconditions

- 使用者為訪客（未登入），Header 顯示 `Signup / Login`
- 系統中已存在一組可登入的帳號（Email 與對應 Password）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 前往 http://automationexercise.com/login | `Login to your account` 區塊顯示 Email Address、Password 欄位與 `Login` 按鈕 |
| 2 | 在 `Email Address` 輸入正確的既存帳號 Email，`Password` 輸入錯誤的密碼，點擊 `Login` | 頁面顯示錯誤訊息 `Your email or password is incorrect!`；URL 仍為 `/login`；Header 仍顯示 `Signup / Login`（未顯示 `Logged in as <name>`） |
| 3 | 在 `Email Address` 輸入未註冊的 Email、`Password` 輸入任意值，點擊 `Login` | 頁面顯示錯誤訊息 `Your email or password is incorrect!`；URL 仍為 `/login`；Header 仍顯示 `Signup / Login` |

### Notes

來源：FR-ACC-04 AC2、§4。PRD 對「錯誤 Email」與「錯誤 Password」定義同一則訊息與同一結果，故合併為單一案例並於步驟 2／3 列出代表值，不拆成兩案。空值與 Email 格式錯誤的驗證不在本案例範圍（PRD §5#2 未定義，見 open_questions）。

## Open Questions

- Email Address 或 Password 留空即點擊 `Login` 時，系統行為與訊息文案為何？是否僅依賴瀏覽器原生的必填驗證？
- Email 格式錯誤（例如缺少 @、含空白）時，是否顯示格式驗證訊息？文案與顯示位置為何？
- Email 比對是否區分大小寫？輸入前後多餘空白是否自動 trim 後再比對？
- 登入失敗後，Email Address 與 Password 欄位的內容是否保留或清空？錯誤訊息的顯示位置為何，以及它在何時消失（下次送出、成功登入或頁面重載）？
- 登入成功後應導向哪個頁面（停留 `/login`、導向首頁或其他頁面）？PRD 僅定義 Header 狀態，未定義導向結果。
- `Logged in as <name>` 中的 `<name>` 取自帳號的哪個欄位（全名／名字／Email）？顯示格式（是否含前後文字或大小寫轉換）為何？
- 已登入的會員再次前往 `/login` 時應如何呈現（導向其他頁面、顯示已登入狀態，或仍顯示登入表單）？
- 登入狀態是否在頁面重新整理與跨頁瀏覽後保持？Session／Cookie 的有效期限為何？
- 未登入訪客直接存取需要登入的頁面時，是否導向 `/login`？導向後是否保留原本的目的地並在登入成功後返回？
- 同一帳號連續多次登入失敗時，是否觸發帳號鎖定、延遲回應或驗證碼等保護機制？
- Password 欄位的字元是否以遮蔽方式顯示？是否提供顯示／隱藏切換？
