---
id: login-smoke
base_url: https://automationexercise.com
---

# Login Smoke

## Case 1: Account - Login (/login): Verify that a guest can log in with an existing account and that the header then shows the logged-in state

```yaml
requirement_ids: [FR-ACC-04, FR-ACC-04-AC1]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- A registered account already exists with a known Email Address and Password
- The tester is a guest: the header shows `Signup / Login`

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Open http://automationexercise.com/login | The `Login to your account` section is displayed with Email Address, Password fields and a `Login` button; the header still shows `Signup / Login` |
| 2 | Enter the existing account's Email Address in the Email Address field and its Password in the Password field | The entered values are accepted by the two fields |
| 3 | Click the `Login` button | The header displays `Logged in as <name>` for the logged-in account and no longer shows `Signup / Login` |

### Notes

Source: FR-ACC-04 AC 1 and the role table in section 2. The exact value substituted for <name> (e.g. registration name vs full name) is not defined by the PRD - see open questions.

## Case 2: Account - Login (/login): Verify that login is rejected with the specified error message when the Email Address or the Password is incorrect

```yaml
requirement_ids: [FR-ACC-04, FR-ACC-04-AC2]
priority: High
test_type: Negative
```

**Severity:** Major

### Preconditions

- A registered account exists: Email Address = <valid registered email>, Password = <its correct password>
- The tester is a guest: the header shows `Signup / Login`

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Open http://automationexercise.com/login | The `Login to your account` section is displayed |
| 2 | Enter the incorrect credential combination in the Email Address and Password fields and click `Login`, using representative values: (a) <valid registered email> with a wrong password, (b) <unregistered email> with any password | The message `Your email or password is incorrect!` is displayed verbatim for each combination |
| 3 | Observe the current page and header after each rejected attempt | The user stays on /login and the header still shows `Signup / Login` (no `Logged in as <name>` state) |

### Notes

Source: FR-ACC-04 AC 2. The two combinations (wrong password, unregistered email) share the same action and expected result, so they are merged into one case as representative values. Where on the page the error text is rendered is not specified - see open questions.

## Case 3: Account - Login (/login): Verify that the `Login to your account` block exposes its title, both input fields and the Login button

```yaml
requirement_ids: [FR-ACC-04]
priority: Medium
test_type: UI
```

**Severity:** Minor

### Preconditions

- The tester is a guest: the header shows `Signup / Login`

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Open http://automationexercise.com/login and locate the login block | The heading text `Login to your account` is displayed verbatim as the title of the login block |
| 2 | Inspect the controls of the login block | An editable `Email Address` input, an editable `Password` input and a button labelled `Login` are present in the block |

### Notes

Source: FR-ACC-04 (block composition) and the verbatim copy list in section 4. This is the only case that asserts the `Login to your account` title text; field behaviour on entry is covered by the functional and negative cases.

## Open Questions

- FR-ACC-04 lists Email Address and Password without any required/format rule: what validation applies when either field is submitted empty or when the Email Address is not a valid email format, and what exact message is shown for each?
- Are the Email Address and Password values compared case-sensitively, and are leading/trailing spaces trimmed before the comparison?
- The verbatim template `Logged in as <name>` does not say which value replaces `<name>` - should it be the name entered at registration, the first name only, or the email address?
- After a successful login, what page should the user land on (stay on /login, go to the home page, or return to the previously requested page)?
- After a failed login attempt, is the Password field cleared and the Email Address retained, and does the error message disappear on the next attempt?
- Where is the `Your email or password is incorrect!` message rendered (above the form, inside the block, as a toast), and how long does it stay visible?
- Does a logged-in session persist across a page refresh or a new tab, and what should happen if a logged-in member navigates to /login directly?
- Is there any lockout, rate limit or CAPTCHA after repeated failed login attempts, and if so what message and waiting period apply?
- Is the Password input masked on screen, and is there a show/hide toggle or any maximum length for either field?
