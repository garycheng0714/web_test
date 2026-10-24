---
id: live-evidence-red
base_url: https://automationexercise.com
---

# Live Evidence Red

## Case 1: Account / Register (Signup Step 1): Verify that submitting a new, unregistered Name and Email on New User Signup! returns to the home page and logs the user in.

```yaml
requirement_ids: [FR-LIVE-01]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- User is a guest (header shows 'Signup / Login')
- Browser is on https://automationexercise.com/login
- The email to be used has never been registered on the site

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Open /login and locate the 'New User Signup!' block. | The 'New User Signup!' block is displayed with a Name field, an Email Address field and a 'Signup' button. |
| 2 | Enter a Name (e.g. 'OC QA') and an unregistered Email Address (e.g. ocqa.<timestamp>@test.com). | The entered values are shown in the Name and Email Address fields. |
| 3 | Click 'Signup'. | The site returns to the home page and the header shows 'Logged in as OC QA'. |

### Notes

Deliberately wrong fixture: the real site opens 'Enter Account Information' and the header still shows 'Signup / Login'. It exists only to force a red automation run and exercise `.scratch/agent-in-ci/issues/07-red-run-evidence.md`; delete it after the run.
