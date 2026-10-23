---
id: register-login
base_url: https://automationexercise.com
---

# Register Login

## Case 1: Account / Register (Signup Step 1): Verify that submitting a new, unregistered Name and Email on New User Signup! opens the Enter Account Information page.

```yaml
requirement_ids: [FR-ACC-01]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- User is a guest (header shows 'Signup / Login')
- Browser is on http://automationexercise.com/login
- The email to be used has never been registered on the site

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Open /login and locate the 'New User Signup!' block. | The 'New User Signup!' block is displayed with a Name field, an Email Address field and a 'Signup' button. |
| 2 | Enter a Name (e.g. 'OC QA') and an unregistered Email Address (e.g. ocqa.<timestamp>@test.com). | The entered values are shown in the Name and Email Address fields. |
| 3 | Click 'Signup'. | The 'Enter Account Information' page is displayed; the account information step is entered rather than staying on /login. |

### Notes

Covers FR-ACC-01 AC1 (source TC1 steps S4~S7). Unregistered-ness of the email is a test-data condition, not an asserted behaviour.

## Case 2: Account / Register (Signup Step 2 + Create Account): Verify that completing Account Information and Address Information and clicking Create Account shows the Account Created! page, and that Continue returns the site logged in.

```yaml
requirement_ids: [FR-ACC-02]
priority: High
test_type: Workflow
```

**Severity:** Critical

### Preconditions

- User is a guest and has already submitted an unregistered Name/Email on New User Signup! and is on the 'Enter Account Information' page (FR-ACC-01 satisfied)

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | In the 'Enter Account Information' block select Title 'Mr.', enter a valid Password (e.g. Password123!), select Day/Month/Year for Date of Birth, and tick 'Sign up for our newsletter!' and 'Receive special offers from our partners!'. | The selected title, password, date of birth and both checkboxes are retained; the Email field still shows the email entered in Signup Step 1. |
| 2 | Fill the 'Address Information' block with valid values: First name, Last name, Company, Address, Address 2, Country, State, City, Zipcode, Mobile Number. | Every entered value is shown in its field and a Country option is selected. |
| 3 | Click 'Create Account'. | The account is created. |
| 4 | Click 'Continue'. | The user is returned to the site in a logged-in state: the header shows 'Logged in as <name>' together with 'Logout' and 'Delete Account'. |

### Notes

Covers FR-ACC-02 AC1 and AC2 in one register workflow (source TC1 steps S9~S16). Expected header text is the PRD's verbatim 'Logged in as <name>' (PRD §6); which of the two entered names is displayed is raised in open_questions.

## Case 3: Account / Register (duplicate email guard): Verify that signing up with an already-registered email is rejected with 'Email Address already exist!' and does not open the account information page.

```yaml
requirement_ids: [FR-ACC-03]
priority: High
test_type: Negative
```

**Severity:** Major

### Preconditions

- A user account already exists for the email used in this case (e.g. created via FR-ACC-01/02 earlier in the same run and not yet deleted)
- User is a guest on /login

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | On /login, in the 'New User Signup!' block enter any Name and the already-registered Email Address. | The entered values are shown in the Name and Email Address fields. |
| 2 | Click 'Signup'. | The error 'Email Address already exist!' is displayed, the user stays on the signup/login page, and the 'Enter Account Information' page is not displayed. |

### Notes

Covers FR-ACC-03 (source TC5 steps S4~S8).

## Case 4: Account / Login (successful): Verify that logging in with a registered email and its correct password logs the user in.

```yaml
requirement_ids: [FR-ACC-04]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- A registered account exists whose email and password are known (e.g. created via FR-ACC-01/02 in the same run)
- User is a guest on /login

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | In the 'Login to your account' block enter the registered Email Address and its correct Password. | The entered values are shown in the Email Address and Password fields. |
| 2 | Click 'Login'. | The user is logged in: the header shows 'Logged in as <name>' together with 'Logout' and 'Delete Account', and no error message is displayed. |

### Notes

Covers FR-ACC-04 AC1 (sources TC2 S4~S8, TC4 S4~S8). PRD §9#4 does not define where the pre-existing account comes from, so it is supplied as a precondition; see open_questions.

## Case 5: Account / Login (failed): Verify that logging in with incorrect credentials shows 'Your email or password is incorrect!' and keeps the user on /login as a guest.

```yaml
requirement_ids: [FR-ACC-04]
priority: High
test_type: Negative
```

**Severity:** Critical

### Preconditions

- A registered account exists and its correct password is known
- User is a guest on /login

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | In the 'Login to your account' block enter the registered Email Address with an incorrect Password. | The entered email and incorrect password are shown in their fields. |
| 2 | Click 'Login'. | The error 'Your email or password is incorrect!' is displayed, the user remains on /login with 'Login to your account' and 'New User Signup!' still visible, and the header still shows 'Signup / Login' (guest, not logged in). |

### Notes

Covers FR-ACC-04 AC2 (source TC3 S4~S8). The PRD defines one message for both a wrong password and an unknown email; whether an unregistered email shows the same message is raised in open_questions.

## Case 6: Account / Logout: Verify that clicking Logout in the header ends the member session and returns the user to /login as a guest.

```yaml
requirement_ids: [FR-ACC-05]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- User is logged in (header shows 'Logged in as <name>' with 'Logout' and 'Delete Account')

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Click 'Logout' in the header. | The user is returned to /login, where 'Login to your account' and 'New User Signup!' are visible and the header shows 'Signup / Login' (guest state, no 'Logged in as ...'). |

### Notes

Covers FR-ACC-05 (source TC4 S9~S10).

## Case 7: Account / Delete Account: Verify that Delete Account shows the Account Deleted! page and that Continue leaves the user in a guest state.

```yaml
requirement_ids: [FR-ACC-06]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- User is logged in (header shows 'Logged in as <name>' with 'Delete Account')

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Click 'Delete Account' in the header. | The 'Account Deleted!' page is displayed together with the text 'Your account has been permanently deleted!'. |
| 2 | Click 'Continue'. | The user is no longer logged in: the header shows 'Signup / Login' and no longer shows 'Logged in as ...' or 'Delete Account'. |

### Notes

Covers FR-ACC-06 (sources TC1 S17~S18, TC2 S9~S10). PRD §9#5 notes this is also the test-cleanup step, so run it last for the account created in this suite.

## Open Questions

- What are the password rules for registration (minimum length, complexity, confirmation field), and what exact message is displayed when the password violates them? (PRD §9#1 states only that 'Password123!' passes.)
- Which fields on New User Signup! (Name, Email Address) are mandatory, and what exact messages appear when they are submitted empty or when the Email Address is not a valid email format? (PRD §9#3: no empty/format validation was observed.)
- Which fields on Enter Account Information and Address Information are mandatory (Title, Password, Date of Birth, and which address fields), and what exact messages appear when a required field is left empty or a field such as Mobile Number or Zipcode is given an invalid format?
- Are email addresses treated as case-insensitive and whitespace-trimmed for duplicate detection at signup and for login (e.g. is 'OC@test.com' the same as 'oc@test.com')? PRD §9#6 lists case only for the CSS-styled headings.
- When the Name entered on New User Signup! differs from the Name entered on the Enter Account Information page, which name is rendered in the header 'Logged in as <name>'?
- Does a login attempt with an email that is not registered show the same 'Your email or password is incorrect!' message as a wrong password, or a different message?
- Is the logged-in state persisted across a page refresh, a new tab, or a browser restart, and is there any session timeout after which the user becomes a guest?
- Is a confirmation dialog or confirmation step required before 'Delete Account' permanently deletes the account?
- What happens on direct URL access outside the stated flow — e.g. a guest opening /delete_account or /logout, or an already logged-in member opening /login: is there a redirect or a specific message? (PRD §2 defines actions only via the header links.)
- Does 'Logout' require a confirmation step, and what happens if Logout is triggered when the session has already expired?
- For login-success tests, where should the pre-existing account come from? PRD §9#4 says the source account is undefined — should a seeded fixture account and credentials be provided instead of creating and deleting a temporary account at runtime?
