---
id: register-login
base_url: https://automationexercise.com
---

# Register Login

## Case 1: Account / Register: Verify that a user can create an account.

```yaml
requirement_ids: [FR-ACC-02]
priority: High
test_type: Workflow
```

**Severity:** Critical

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Click 'Create Account'. | The 'Account Created!' page is displayed with the success text. |
| 2 | Click 'Continue'. | The header shows 'Logged in as <name>' with 'Logout' and 'Delete Account'. |

### Notes

Deliberate FAIL variant for the live required-check test.
