---
id: register-login
base_url: https://automationexercise.com
---

# Register Login

## Case 1: Account / Register: Verify that submitting a new, unregistered Name and Email on New User Signup! opens the Enter Account Information page.

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

Live PASS variant for the required-check test.
