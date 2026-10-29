---
id: register-login
base_url: https://automationexercise.com
---

# Register Login

## Case 1: Account / Registration – Step 1 (Name + Email): Verify that a guest submitting a name and an unregistered email in New User Signup! is taken to the Enter Account Information page

```yaml
requirement_ids: [FR-ACC-01]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- User is not logged in (header shows Signup / Login).
- The email address to be used is not registered on the site.

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Open http://automationexercise.com | Home page is displayed and the header shows the Signup / Login link. |
| 2 | Click the Signup / Login link in the header | The /login page is displayed with a Login to your account section and a New User Signup! section. |
| 3 | In the New User Signup! section enter a Name and an unregistered Email Address | Both fields accept the entered values. |
| 4 | Click the Signup button | The Enter Account Information page is displayed, containing the Address Information section and the Create Account button; the URL is no longer /login. |

### Notes

Source: TCr1-S4~S7 (Register User) / prd.md FR-ACC-01. Header assertion for the guest role is folded into step 1 of this case.

## Case 2: Account / Registration – Step 2 (Account + Address information): Verify that completing the account and address information and clicking Create Account produces the Account Created! confirmation and leaves the user logged in after Continue

```yaml
requirement_ids: [FR-ACC-02]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- The Enter Account Information page is open for a new, unregistered email (result of FR-ACC-01).
- The email carried over from step 1 is unique.

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | On the Enter Account Information page fill the account information: Title, Name, Password, Date of Birth, and leave/keep the newsletter and partner-offer opt-ins as desired | All entered values are accepted and displayed in their controls. |
| 2 | Fill the Address Information section: First name, Last name, Company, Address, Address 2, Country, State, City, Zipcode, Mobile Number | All entered values are accepted and displayed in their controls. |
| 3 | Click the Create Account button | The Account Created! page is displayed with the text 'Congratulations! Your new account has been successfully created!' and a Continue link. |
| 4 | Click the Continue link | The user is returned to the site in a logged-in state: the header shows 'Logged in as <name>' together with the Logout and Delete Account links. |

### Notes

Source: TCr1-S9~S16 (Register User) / prd.md FR-ACC-02. Which fields are actually mandatory and any format rules are undefined in the PRD (see open_questions), so the case fills every documented field.

## Case 3: Account / Registration – Duplicate email protection: Verify that signing up with an already registered email shows the duplicate-email error and does not open the account information page

```yaml
requirement_ids: [FR-ACC-03]
priority: High
test_type: Negative
```

**Severity:** Major

### Preconditions

- User is not logged in.
- An account already exists for a known email address (e.g. created via FR-ACC-01/FR-ACC-02).

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Open /login and, in the New User Signup! section, enter any Name together with the email address of the already registered account | Both fields accept the entered values. |
| 2 | Click the Signup button | The error message 'Email Address already exist!' is displayed. |
| 3 | Observe the page after the error is displayed | The user remains on the /login page; the Enter Account Information page is not displayed. |

### Notes

Source: TCr5-S4~S8 (Register existing email) / prd.md FR-ACC-03.

## Case 4: Account / Login – Valid credentials: Verify that logging in with correct credentials logs the user in and the header shows Logged in as <name>

```yaml
requirement_ids: [FR-ACC-04]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- A registered account exists with known email and password.
- User is not logged in.

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Open /login | The Login to your account section with Email Address, Password and the Login button is displayed. |
| 2 | Enter the registered email address and its correct password in the Login to your account section | The credentials are accepted in their fields. |
| 3 | Click the Login button | The user is logged in: the header shows 'Logged in as <name>' with the Logout and Delete Account links, and no login error message is displayed. |

### Notes

Source: TCr2-S4~S8, TCr4-S4~S8 (Login correct) / prd.md FR-ACC-04 AC1.

## Case 5: Account / Login – Invalid credentials: Verify that logging in with incorrect credentials shows the login error and keeps the user on /login as a guest

```yaml
requirement_ids: [FR-ACC-04]
priority: High
test_type: Negative
```

**Severity:** Major

### Preconditions

- A registered account exists with known email and password.
- User is not logged in.

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Open /login and enter incorrect credentials in the Login to your account section | The entered values are accepted in their fields. |
| 2 | Click the Login button | The error message 'Your email or password is incorrect!' is displayed and the user stays on the /login page. |
| 3 | Observe the header and page state | The user remains a guest: the header shows Signup / Login and not 'Logged in as <name>', and the Login to your account / New User Signup! sections remain visible. |

### Notes

Source: TCr3-S4~S8 (Login incorrect) / prd.md FR-ACC-04 AC2. Representative invalid inputs to cover in the same case (same expected result): registered email + wrong password; unregistered email + any password.

## Case 6: Account / Logout: Verify that a logged-in member clicking Logout returns to /login as a guest

```yaml
requirement_ids: [FR-ACC-05]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- User is logged in (header shows 'Logged in as <name>' with Logout and Delete Account links).

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Click the Logout link in the header | The /login page is displayed containing the Login to your account and New User Signup! sections. |
| 2 | Observe the header after logout | The header no longer shows 'Logged in as <name>', Logout or Delete Account; it shows the Signup / Login link (guest state). |

### Notes

Source: TCr4-S9~S10 (Logout) / prd.md FR-ACC-05.

## Case 7: Account / Delete Account: Verify that a logged-in member deleting the account sees the Account Deleted! confirmation and is returned to guest state after Continue

```yaml
requirement_ids: [FR-ACC-06]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- User is logged in with an account that may be permanently deleted.

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Click the Delete Account link in the header | The Account Deleted! page is displayed with the text 'Your account has been permanently deleted!' and a Continue link. |
| 2 | Click the Continue link | The user is no longer logged in: the header shows the Signup / Login link, and 'Logged in as <name>', Logout and Delete Account are no longer displayed. |

### Notes

Source: TCr1-S17~S18, TCr2-S9~S10 / prd.md FR-ACC-06. No confirmation step before deletion is described in the PRD (see open_questions).

## Open Questions

- What are the password requirements for registration (minimum length, character classes), and what message is shown when a password does not meet them? The PRD defines no rule.
- Which registration fields are mandatory, and what messages/behaviour are shown for empty or malformed input (e.g. Mobile Number format, Zipcode format, incomplete Date of Birth, missing Name/Address)?
- Is email uniqueness and login case-sensitive — e.g. are 'User@Example.com' and 'user@example.com' the same account for the 'Email Address already exist!' check and for login?
- Are Name and Email values trimmed of leading/trailing whitespace on signup and login, and does a trailing space in an email cause a duplicate-account or login failure?
- Does a login attempt with an unregistered email show the same 'Your email or password is incorrect!' message as a wrong password, or is a distinguishable message intended?
- Is the account deleted immediately without a confirmation prompt, and is any recovery or grace period intended after 'Your account has been permanently deleted!'?
- After an account is deleted, can the same email address be used to register a new account immediately, and are previously used credentials rejected?
- What should happen when a logged-in member navigates directly to /login or the signup section — is a redirect, the login page, or an error expected?
- Is the login session remembered across browser restarts (persistent cookie) or does it end when the browser is closed?
