---
id: register-login
base_url: https://automationexercise.com
---

# Register Login

## Case 1: Account / Registration – Step 1 (New User Signup!): Verify that submitting a Name and an unregistered Email Address in the New User Signup! block opens the Enter Account Information page

```yaml
requirement_ids: [FR-ACC-01]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- User is not logged in (guest) and is on http://automationexercise.com/login
- An email address that has never been registered on the site is available for use

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Open /login and inspect the page | Page shows a 'Login to your account' section and a separate 'New User Signup!' section; the signup section contains a Name field, an Email Address field and a 'Signup' button |
| 2 | In the 'New User Signup!' section enter Name = 'OC QA' and Email Address = an unregistered email (e.g. oc.qa.<timestamp>@example.com), then click 'Signup' | The 'Enter Account Information' page is displayed, containing the 'Enter Account Information' block and the 'Address Information' block with a 'Create Account' button |
| 3 | Check the Name and Email Address shown on the 'Enter Account Information' page | Name shows 'OC QA' and Email Address shows the email entered in the previous step (values carried over from signup step 1) |

### Notes

Source: TCr1-S4~S7 (Register User). Covers FR-ACC-01 AC1.

## Case 2: Account / Registration – Step 2 (Account & Address Information): Verify that completing the account and address information and clicking Create Account creates the account, shows the Account Created! page, and that Continue returns the user to a logged-in session

```yaml
requirement_ids: [FR-ACC-02]
priority: High
test_type: Workflow
```

**Severity:** Critical

### Preconditions

- The 'Enter Account Information' page is open for an unregistered email (reached via New User Signup! with a valid Name and Email)
- A password meeting the site's rules is available (e.g. Password123!)

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Select Title 'Mr.' (or 'Mrs.'), fill Password, Date of Birth (Day/Month/Year), and the address fields First name, Last name, Company, Address, Address 2, Country, State, City, Zipcode and Mobile Number | All entered values are accepted and remain displayed in their respective fields |
| 2 | Click 'Create Account' | The 'Account Created!' page is displayed showing the text 'Congratulations! Your new account has been successfully created!' and a 'Continue' link |
| 3 | Click 'Continue' | The user is returned to the site in a logged-in state and the header displays 'Logged in as <name>' using the name given at signup |
| 4 | Inspect the header as a logged-in user | Header shows 'Logged in as <name>' together with 'Logout' and 'Delete Account' links instead of 'Signup / Login' |

### Notes

Source: TCr1-S9~S16 (Register User). Covers FR-ACC-02 AC1 and AC2. Field-level format validation is not specified by the PRD (see open questions).

## Case 3: Account / Registration – Duplicate Email Protection: Verify that signing up with an already registered email address is rejected with the error 'Email Address already exist!' and does not open the account information page

```yaml
requirement_ids: [FR-ACC-03]
priority: High
test_type: Negative
```

**Severity:** Major

### Preconditions

- An account already exists with email E (e.g. created by the registration flow)
- User is on /login as a guest

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | In the 'New User Signup!' section enter Name = 'OC QA' and Email Address = E (the already registered email), then click 'Signup' | The error message 'Email Address already exist!' is displayed |
| 2 | Observe the page and URL after the error | The user remains on /login with the 'Login to your account' and 'New User Signup!' sections still visible; the 'Enter Account Information' page is not displayed |

### Notes

Source: TCr5-S4~S8 (Register existing email). Covers FR-ACC-03 AC. Email case sensitivity / trimming on this uniqueness check is undefined (see open questions).

## Case 4: Account / Login: Verify that logging in with a correct email and password authenticates the user and shows 'Logged in as <name>' in the header

```yaml
requirement_ids: [FR-ACC-04]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- A registered account exists with a known valid email and password
- User is on /login as a guest

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | In the 'Login to your account' section enter the valid Email Address and Password, then click 'Login' | The user is logged in and the header displays 'Logged in as <name>' matching the account's name |
| 2 | Check the login/signup state of the page after logging in | The header no longer shows the 'Signup / Login' link and instead shows 'Logged in as <name>', 'Logout' and 'Delete Account' |

### Notes

Source: TCr2-S4~S8, TCr4-S4~S8 (Login correct). Covers FR-ACC-04 AC1.

## Case 5: Account / Login: Verify that logging in with incorrect credentials shows 'Your email or password is incorrect!' and keeps the user on /login as a guest

```yaml
requirement_ids: [FR-ACC-04]
priority: High
test_type: Negative
```

**Severity:** Major

### Preconditions

- A registered account exists with a known valid email and password
- User is on /login as a guest

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | In the 'Login to your account' section enter a registered Email Address with a wrong Password (also check the representative case of an unregistered email address), then click 'Login' | The error message 'Your email or password is incorrect!' is displayed |
| 2 | Observe the page, URL and header after the failed login | The user stays on /login with 'Login to your account' and 'New User Signup!' visible; the header still shows 'Signup / Login' and no 'Logged in as <name>' text appears |

### Notes

Source: TCr3-S4~S8 (Login incorrect). Covers FR-ACC-04 AC2. Behaviour for empty email/password is not specified by the PRD (see open questions).

## Case 6: Account / Logout: Verify that clicking Logout ends the session and returns the user to /login in guest state

```yaml
requirement_ids: [FR-ACC-05]
priority: Medium
test_type: Functional
```

**Severity:** Major

### Preconditions

- A user is logged in (header shows 'Logged in as <name>')

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Click the 'Logout' link in the site header | The user is returned to /login, where the 'Login to your account' and 'New User Signup!' sections are visible |
| 2 | Inspect the header after logout | Header shows the 'Signup / Login' link again; 'Logged in as <name>', 'Logout' and 'Delete Account' are no longer displayed |

### Notes

Source: TCr4-S9~S10 (Logout). Covers FR-ACC-05 AC.

## Case 7: Account / Delete Account: Verify that Delete Account permanently deletes the account, shows the Account Deleted! page, and that Continue returns the user to guest state

```yaml
requirement_ids: [FR-ACC-06]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- A user is logged in with an account that may be deleted (e.g. the account created during registration)

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Click the 'Delete Account' link in the site header | The 'Account Deleted!' page is displayed showing the text 'Your account has been permanently deleted!' and a 'Continue' link |
| 2 | Click 'Continue' | The user is no longer logged in and the header shows the 'Signup / Login' link instead of 'Logged in as <name>' |

### Notes

Source: TCr1-S17~S18, TCr2-S9~S10 (Register User / Login correct cleanup step). Covers FR-ACC-06 AC. This feature doubles as the test-data cleanup mechanism.

## Open Questions

- 密碼規則未定義：註冊時 Password 的最小長度／複雜度要求為何？不符合時是否阻止建立帳號、顯示什麼訊息？
- 註冊 Step 2 各欄位的必填與格式規則未定義：Name、Password、Date of Birth、Address、Country、State、City、Zipcode、Mobile Number 哪些為必填？空值或格式錯誤（如 Zipcode 非數字、Mobile Number 格式、Email 格式）時的錯誤訊息與是否阻止建立？
- Email 的比對規則未定義：註冊唯一性檢查與登入比對是否忽略大小寫（Foo@x.com vs foo@x.com）與前後空白？若僅大小寫不同，Signup 是否仍顯示 `Email Address already exist!`？
- 註冊的兩步驟之間若中途離開：Step 1 通過後未按 Create Account 即離開或直接以網址造訪帳號資訊頁，是否會留下半成品帳號或 session？
- 同一個未註冊 Email 在 Step 1 通過後、按下 Create Account 前被他人註冊時，Create Account 的結果與訊息為何？
- 登入時 Email 或 Password 留空即送出：是否顯示 `Your email or password is incorrect!`、單一欄位的必填訊息，或客户端直接阻擋？
- 已登入會員直接存取 /login、/ 或註冊區塊時，是否被導向其他頁面或隱藏登入/註冊表單（權限轉導規則）？
- Session 持續性未定義：登入後重新整理頁面或關閉再開瀏覽器，登入狀態是否維持？是否有逾時登出？
- Delete Account 是否需要二次確認（確認對話框）？PRD 未描述，誤點是否會直接永久刪除？
- 刪除帳號後的行為未定義：被刪除的 Email 是否可立即用於重新註冊？以原帳密登入應顯示 `Your email or password is incorrect!` 還是其他訊息？
- `Sign up for our newsletter!` 與 `Receive special offers from our partners!` 兩個 opt-in checkbox 是否必勾？勾選／未勾選對建立帳號或後續行為有無影響？
