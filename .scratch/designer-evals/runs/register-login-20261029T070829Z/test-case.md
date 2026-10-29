---
id: register-login
base_url: https://automationexercise.com
---

# Register Login

## Case 1: 會員 ACC - 註冊 Step 1（Name + Email）: Verify that a guest who submits an unregistered Name and Email in the `New User Signup!` block is taken to the `Enter Account Information` page

```yaml
requirement_ids: [FR-ACC-01]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- 使用者為訪客（未登入）
- 已備妥一組系統中不存在的 Email（送出路徑前確認該 Email 尚無對應帳號）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 開啟 http://automationexercise.com | 首頁載入，全站 Header 顯示 `Signup / Login` 連結（訪客狀態，無 `Logged in as`／`Logout`／`Delete Account`） |
| 2 | 點擊 Header 的 `Signup / Login` | 進入 `/login`，頁面依序顯示 `Login to your account` 區塊、`OR`、`New User Signup!` 區塊 |
| 3 | 在 `New User Signup!` 的 Name 欄輸入 `OC QA`，Email Address 欄輸入一組未註冊的 Email | 兩個欄位接受輸入並顯示所輸入內容 |
| 4 | 點擊 `Signup` 按鈕 | 離開 `/login` 並進入帳號資訊頁，頁面顯示 `Enter Account Information` 與 `Address Information` 兩個區塊，以及 `Create Account` 按鈕 |

### Notes

來源 TCr1-S4~S7。此步驟的 Email 後續供 FR-ACC-02 案例沿用（可於同一輪執行串接）。

## Case 2: 會員 ACC - 註冊 Step 2（帳號資訊 + 地址資訊）: Verify that completing the account and address information and clicking `Create Account` creates the account, shows the `Account Created!` page, and that `Continue` returns the user in a logged-in state

```yaml
requirement_ids: [FR-ACC-02]
priority: High
test_type: Workflow
```

**Severity:** Critical

### Preconditions

- 已於 `New User Signup!` 以未註冊的 Name / Email 送出，目前停在 `Enter Account Information` 頁
- 準備一組符合系統接受的 Password（實測 `Password123!` 可通過，密碼規則未定義，見 open questions）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 選取 Title 為 `Mr.`（或 `Mrs.`），檢視 Name 與 Email 欄位 | Title radio 呈已選取狀態；Name 與 Email 為 Step 1 送出的值，且 Email 欄位不可編輯（disabled） |
| 2 | 輸入 Password，並由 Day / Month / Year 下拉選取 Date of Birth | Password 顯示為遮蔽輸入；Date of Birth 三個下拉選定後顯示所選日／月／年 |
| 3 | 填寫 Address Information 全部欄位：First name、Last name、Company、Address、Address 2、Country（下拉選一值）、State、City、Zipcode、Mobile Number | 各文字欄位接受並保留輸入值；Country 顯示所選國家 |
| 4 | 點擊 `Create Account` 按鈕 | 顯示 `Account Created!` 頁面，包含文字 `Congratulations! Your new account has been successfully created!`，並有 `Continue` 連結 |
| 5 | 點擊 `Continue` 連結 | 進入網站頁面且為已登入狀態：Header 顯示 `Logged in as OC QA`，並出現 `Logout` 與 `Delete Account` 連結，不再顯示 `Signup / Login` |

### Notes

來源 TCr1-S9~S16。Address 為單行／多行欄位不影響驗證；`Sign up for our newsletter!` 與 `Receive special offers from our partners!` 勾選後的可觀察效果 PRD 未定義（見 open questions），故不列入預期結果。

## Case 3: 會員 ACC - 註冊重複 Email 防護: Verify that submitting an already-registered Email in the `New User Signup!` block shows `Email Address already exist!` and does not open the account information page

```yaml
requirement_ids: [FR-ACC-03]
priority: High
test_type: Negative
```

**Severity:** Major

### Preconditions

- 使用者為訪客（未登入）
- 系統中已存在一個帳號，且已知其註冊 Email

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 前往 `/login` | 頁面顯示 `New User Signup!` 區塊（含 Name、Email Address 欄位與 `Signup` 按鈕） |
| 2 | 在 `New User Signup!` 的 Name 欄輸入任意名稱，Email Address 欄輸入已註冊的 Email，並點擊 `Signup` | 頁面顯示錯誤訊息 `Email Address already exist!`；使用者停留在 `/login`，未顯示 `Enter Account Information` 頁，亦未被登入（Header 仍顯示 `Signup / Login`） |

### Notes

來源 TCr5-S4~S8。對照 FR-ACC-01 未註冊 Email 應成功進入下一頁，兩者互為對照組。

## Case 4: 會員 ACC - 登入: Verify that logging in with valid credentials puts the user in a logged-in state

```yaml
requirement_ids: [FR-ACC-04]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- 使用者為訪客（未登入），位於任一頁面
- 系統中存在一筆已註冊帳號（Name = `OC QA`），且已知其 Email 與 Password

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 前往 `/login` | 頁面顯示 `Login to your account` 區塊，含 Email Address、Password 欄位與 `Login` 按鈕 |
| 2 | 於 Email Address 輸入該帳號 Email、Password 輸入正確密碼 | 兩個欄位接受輸入；Password 顯示為遮蔽輸入 |
| 3 | 點擊 `Login` 按鈕 | 登入成功：Header 顯示 `Logged in as OC QA`，並顯示 `Logout` 與 `Delete Account` 連結，不再顯示 `Signup / Login` |

### Notes

來源 TCr2-S4~S8、TCr4-S4~S8。既有帳號可由 FR-ACC-02 案例建立後沿用。

## Case 5: 會員 ACC - 登入: Verify that logging in with an incorrect password shows the error and keeps the user on the login page as a guest

```yaml
requirement_ids: [FR-ACC-04]
priority: High
test_type: Negative
```

**Severity:** Major

### Preconditions

- 使用者為訪客（未登入）
- 系統中存在一筆已註冊帳號，且已知其 Email

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 前往 `/login` | 頁面顯示 `Login to your account` 區塊（Email Address、Password、`Login`） |
| 2 | 於 Email Address 輸入該已註冊 Email，Password 輸入錯誤的密碼 | 欄位接受輸入，Password 以遮蔽顯示 |
| 3 | 點擊 `Login` 按鈕 | 顯示錯誤訊息 `Your email or password is incorrect!`；使用者停留在 `/login`（仍可見 `Login to your account` 與 `New User Signup!`），Header 仍為 `Signup / Login`，未出現 `Logged in as` |

### Notes

來源 TCr3-S4~S8。PRD 僅定義「錯誤帳密」單一情境與單一文案，故不細分密碼錯誤與帳號不存在。

## Case 6: 會員 ACC - 登出: Verify that a logged-in member clicking `Logout` in the header returns to `/login` in guest state

```yaml
requirement_ids: [FR-ACC-05]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 使用者已以有效帳密登入，Header 顯示 `Logged in as OC QA`

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 點擊 Header 的 `Logout` 連結 | 導向 `/login`，頁面可見 `Login to your account` 與 `New User Signup!` 兩個區塊 |
| 2 | 檢視 Header 狀態 | Header 顯示 `Signup / Login`，不再顯示 `Logged in as OC QA`、`Logout`、`Delete Account` |

### Notes

來源 TCr4-S9~S10。登出後 session 是否於重整／新分頁維持未定義（見 open questions）。

## Case 7: 會員 ACC - 刪除帳號: Verify that a logged-in member deleting the account sees the `Account Deleted!` page and is returned to guest state after `Continue`

```yaml
requirement_ids: [FR-ACC-06]
priority: High
test_type: Workflow
```

**Severity:** Critical

### Preconditions

- 使用者已以即將刪除的帳號登入，Header 顯示 `Logged in as OC QA`

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 點擊 Header 的 `Delete Account` 連結 | 顯示 `Account Deleted!` 頁面，包含文字 `Your account has been permanently deleted!`，並有 `Continue` 連結 |
| 2 | 點擊 `Continue` 連結 | 離開已登入狀態：Header 顯示 `Signup / Login`，不再顯示 `Logged in as OC QA`、`Logout`、`Delete Account` |

### Notes

來源 TCr1-S17~S18、TCr2-S9~S10。Delete Account 同時為測試資料清理手段（PRD §11.2#10）。刪除後該 Email 是否可立即重新註冊未定義（見 open questions）。

## Open Questions

- 密碼規則未定義：註冊時 Password 的最短長度與複雜度要求為何？不符合時顯示什麼訊息、是否阻止建立帳號？
- 註冊 Step 1 與 Step 2 的必填／格式驗證未定義：Name、Email（含格式錯誤）、地址欄位留空或格式不合法時，系統阻擋行為與錯誤文案為何？
- Email 唯一性與登入比對是否區分大小寫、是否去除前後空白（例如 `OC@QA.com` 與 `oc@qa.com ` 是否視為同一帳號）？
- `Logged in as <name>` 中的 `<name>` 應取註冊 Step 1 的 Name，或 First name / Last name 的組合？
- 登入成功後 Session 是否在頁面重整或新開分頁後仍維持？逾期時間與是否支援多裝置同時登入？
- 訪客直接開啟 `/logout` 或 `/delete_account`（未登入狀態）時，系統行為為何：重導向到哪個頁面、顯示什麼訊息？
- 登入失敗是否累計次數並鎖定帳號或加入節流？錯誤訊息是否因「帳號不存在」與「密碼錯誤」而不同？
- 刪除帳號後，同一 Email 是否可立即重新註冊？先前登入憑證是否立即失效？
- `Sign up for our newsletter!` 與 `Receive special offers from our partners!` 勾選後有何可觀察效果？（本 PRD 將訂閱列為 Out of Scope，需確認是否需任何驗證）
- 在 `Account Created!` 頁尚未點 `Continue` 時，使用者是否已算登入（Header 是否已顯示 `Logged in as`）？
