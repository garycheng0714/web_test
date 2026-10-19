---
id: register-login
base_url: https://automationexercise.com
---

# Register Login

## Case 1: Account / Signup – Step 1 (Name + Email): Verify that a guest who signs up with an unregistered email is taken to the Enter Account Information page

```yaml
requirement_ids: [FR-ACC-01]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- User is a guest (not logged in)
- The email address to be used is not registered on the site

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Navigate to http://automationexercise.com/login | The /login page displays both the 'Login to your account' block and the 'New User Signup!' block. |
| 2 | In the 'New User Signup!' block, enter Name (e.g. OC QA) and an unregistered Email Address | The Name and Email Address fields accept the entered values. |
| 3 | Click the Signup button | The browser navigates to the account information page displaying the 'Enter Account Information' and 'Address Information' sections; the 'New User Signup!' block is no longer shown. |

### Notes

Source: TCr1-S4~S7, FR-ACC-01 AC1.

## Case 2: Account / Signup – Step 2 (Account + Address info, Create Account): Verify that completing account information and address information creates the account, and Continue leaves the user logged in

```yaml
requirement_ids: [FR-ACC-02]
priority: High
test_type: Workflow
```

**Severity:** Critical

### Preconditions

- User is on the 'Enter Account Information' page reached via New User Signup! with an unregistered email

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Fill the account information section (Title, Name, Password, Date of Birth Day/Month/Year) | All account information fields accept the entered values. |
| 2 | Fill the address information section (First name, Last name, Company, Address, Address 2, Country, State, City, Zipcode, Mobile Number) | All address information fields accept the entered values. |
| 3 | Click the Create Account button | 'Account Created!' page is displayed containing 'Congratulations! Your new account has been successfully created!' |
| 4 | Click the Continue link on the account created page | User returns to the site in logged-in state; the header shows 'Logged in as <name>' along with Logout and Delete Account links. |

### Notes

Source: TCr1-S9~S16; FR-ACC-02 AC1 and AC2 are the same sequential flow and are covered in one case.

## Case 3: Account / Signup – Duplicate Email protection: Verify that signing up with an email address that is already registered is rejected

```yaml
requirement_ids: [FR-ACC-03]
priority: High
test_type: Negative
```

**Severity:** Major

### Preconditions

- User is a guest (not logged in)
- An account already exists for email X

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Navigate to http://automationexercise.com/login | The 'New User Signup!' block with Name and Email Address fields and the Signup button is displayed. |
| 2 | Enter a Name and the already-registered email X, then click Signup | The error 'Email Address already exist!' is displayed and the Enter Account Information page is NOT shown; the user remains on the signup form. |

### Notes

Source: TCr5-S4~S8, FR-ACC-03 AC.

## Case 4: Account / Login: Verify that logging in with correct credentials establishes a logged-in session

```yaml
requirement_ids: [FR-ACC-04]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- User is a guest (not logged in)
- A registered account exists with a known email and password (e.g. created via FR-ACC-01/02)

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Navigate to http://automationexercise.com/login | The 'Login to your account' block with Email Address and Password fields and the Login button is displayed. |
| 2 | Enter the registered Email Address and the correct Password, then click Login | Login succeeds and the header shows 'Logged in as <name>' with Logout and Delete Account links. |

### Notes

Source: TCr2-S4~S8, TCr4-S4~S8, FR-ACC-04 AC1.

## Case 5: Account / Login: Verify that logging in with incorrect credentials is rejected and the user stays on the login page

```yaml
requirement_ids: [FR-ACC-04]
priority: High
test_type: Negative
```

**Severity:** Major

### Preconditions

- User is a guest (not logged in)
- A registered account exists with a known email and password

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Navigate to http://automationexercise.com/login | The 'Login to your account' block is displayed. |
| 2 | Enter a registered/known Email Address with an incorrect Password (or a non-registered email with any password), then click Login | The error 'Your email or password is incorrect!' is displayed and the user remains on /login with the 'Login to your account' and 'New User Signup!' blocks still visible; the header does NOT show 'Logged in as <name>'. |

### Notes

Source: TCr3-S4~S8, FR-ACC-04 AC2.

## Case 6: Account / Logout: Verify that a logged-in member can log out and is returned to the guest state on the login page

```yaml
requirement_ids: [FR-ACC-05]
priority: Medium
test_type: Functional
```

**Severity:** Major

### Preconditions

- User is logged in (header shows 'Logged in as <name>')

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Click the Logout link in the site header | The user is returned to /login, where 'Login to your account' and 'New User Signup!' are both visible. |
| 2 | Inspect the site header | The header shows the guest state ('Signup / Login') and no longer shows 'Logged in as <name>', Logout, or Delete Account. |

### Notes

Source: TCr4-S9~S10, FR-ACC-05 AC.

## Case 7: Account / Delete Account: Verify that a logged-in member can delete their account and returns to the guest state

```yaml
requirement_ids: [FR-ACC-06]
priority: Medium
test_type: Functional
```

**Severity:** Major

### Preconditions

- User is logged in (header shows 'Logged in as <name>')

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Click the Delete Account link in the site header | 'Account Deleted!' page is displayed containing 'Your account has been permanently deleted!' |
| 2 | Click the Continue link on the account deleted page | The user is no longer logged in; the header shows the guest state ('Signup / Login') instead of 'Logged in as <name>'. |

### Notes

Source: TCr1-S17~S18, TCr2-S9~S10, FR-ACC-06 AC.

## Open Questions

- What are the password rules for signup (minimum length, required character classes, maximum length), and what message is shown if a password violates them?
- Which fields on the account information and address information pages are mandatory, and what validation messages appear when a mandatory field on the New User Signup! block or the Enter Account Information page is left empty?
- What email format validation applies on the signup and login forms, and what message is shown for a malformed email address?
- Is email uniqueness case-sensitive and are leading/trailing spaces trimmed (e.g. is 'A@X.com' treated as the same account as 'a@x.com')?
- Is the email from signup Step 1 re-validated when Create Account is clicked — i.e. what happens if that email becomes registered between Step 1 and Step 2?
- Are there format or length constraints on Mobile Number, Zipcode, Name, and address fields, and what messages are shown for invalid values?
- What happens if a logged-in member navigates directly to /login — is the page shown, or are they redirected?
- Does clicking Delete Account require a confirmation step before the account is permanently removed?
- Does the logged-in session survive a page refresh or browser restart, and does Logout invalidate the session so the browser Back button cannot restore the logged-in state?
- Is login comparison of the email and password case-sensitive?
- After an account is deleted, can the same email address be reused immediately to register a new account?
