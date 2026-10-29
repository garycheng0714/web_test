---
id: login-smoke
base_url: https://automationexercise.com
---

# Login Smoke

## Case 1: 登入 Login (/login): Verify that the /login page presents the 'Login to your account' section with an Email Address field, a Password field, and a Login button.

```yaml
requirement_ids: [FR-ACC-04]
priority: Medium
test_type: UI
```

**Severity:** Minor

### Preconditions

- Browser session is a guest (not logged in) and the Header shows `Signup / Login`
- http://automationexercise.com is reachable

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Navigate to http://automationexercise.com/login | The `/login` page loads and a section titled `Login to your account` is displayed (text matches verbatim). |
| 2 | Inspect the `Login to your account` section | An `Email Address` input, a `Password` input, and a `Login` button are present and visible inside the section. |

### Notes

Source: PRD §3 FR-ACC-04 bullet 1 (login block contents) and §4 verbatim text list. Section title `Login to your account` is taken verbatim from §4.

## Case 2: 登入 Login (/login): Verify that a member logs in successfully with a correct Email Address and Password and the Header switches to the logged-in state.

```yaml
requirement_ids: [FR-ACC-04]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- An existing account is known to the tester with its Email Address, Password, and displayed name <name>
- Browser session is a guest (not logged in) on http://automationexercise.com

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Open http://automationexercise.com/login | The `Login to your account` section is displayed with the Email Address and Password fields and the `Login` button. |
| 2 | Enter the existing account's Email Address in the Email Address field and its Password in the Password field | The entered values appear in the corresponding fields; the `Login` button remains available to click. |
| 3 | Click the `Login` button | The Header changes to display `Logged in as <name>` for that account (text matches verbatim pattern, `<name>` is the account's name), the guest `Signup / Login` link is no longer the active account state, and no `Your email or password is incorrect!` message is displayed. |

### Notes

Source: PRD §3 FR-ACC-04 AC1 and §4 verbatim header text. AC1 does not state the post-login landing page, so no URL assertion is made beyond the Header state.

## Case 3: 登入 Login (/login): Verify that login is rejected with the verbatim error message and the user stays on /login when the Email Address or Password is incorrect.

```yaml
requirement_ids: [FR-ACC-04]
priority: High
test_type: Negative
```

**Severity:** Major

### Preconditions

- An existing account with a known Email Address and Password is available for the wrong-password variant
- Browser session is a guest on http://automationexercise.com/login

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Open http://automationexercise.com/login | The `Login to your account` section is displayed. |
| 2 | Enter incorrect credentials — variants to cover: (a) an unregistered Email Address with any Password, (b) a registered Email Address with an incorrect Password — then note both variants produce the same outcome | The entered values appear in the corresponding fields. |
| 3 | Click the `Login` button | The message `Your email or password is incorrect!` is displayed (text matches verbatim), the page remains on `/login`, and the Header does not show `Logged in as <name>` (guest state `Signup / Login` persists). |

### Notes

Source: PRD §3 FR-ACC-04 AC2 and §4 verbatim failure message. The two variants (wrong email / wrong password) are merged because AC2 defines one identical message and behaviour; they are listed as representative inputs rather than separate cases.

## Open Questions

- 當 Email Address 或 Password 欄位為空白即點擊 `Login` 時，應顯示什麼訊息？是否需要必填驗證？（PRD §5 假設 2 未涵蓋，§4 也未提供對應文案）
- 當 Email 格式不合法（例如缺少 `@`）時，是否有前端格式驗證與專屬訊息，或一律顯示 `Your email or password is incorrect!`？
- 登入驗證是否區分 Email 大小寫？是否會自動 trim Email 前後的空白？
- 登入成功後應停留在 `/login` 還是導向首頁／帳號頁？成功後先前顯示的登入失敗訊息是否需清除？
- Header 中 `Logged in as <name>` 的 `<name>` 來源與顯示規則為何（全名或暱稱？大小寫與截斷規則）？
- 登入失敗後，Email Address 與 Password 欄位是否保留原輸入？使用者重新輸入時錯誤訊息是否應立即消失？
- 已登入的會員再次前往 `/login` 時的預期行為為何（顯示登入表單、導向其他頁面，或顯示其他訊息）？
- 登入狀態在重新整理頁面或導覽至其他頁面後是否維持，PRD 是否要求 session 持續有效？
- Password 欄位是否需以遮蔽字元顯示輸入內容？PRD 未描述該顯示行為。
- 連續多次登入失敗是否有帳號鎖定、驗證碼或頻率限制機制？
