---
id: live-evidence
base_url: https://automationexercise.com
---

# Live Evidence

## Case 1: Account Registration – New User Signup (Step 1): Verify that a guest submitting a Name and an unregistered Email Address via the New User Signup! section is taken to the Enter Account Information page

```yaml
requirement_ids: [FR-ACC-01]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- The site https://automationexercise.com is reachable.
- The tester is a guest (not logged in); the site header shows `Signup / Login`.
- The Email Address to be used has never been registered on the site (e.g. a freshly generated unique address).

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Navigate to https://automationexercise.com/login and locate the signup block. | The login page is displayed and contains a section whose title text is `New User Signup!`, with a Name field, an Email Address field, and a button labelled `Signup`. |
| 2 | In the `New User Signup!` section, type a name (e.g. `QA Tester`) into the Name field and type an unregistered email address (e.g. `qa.step1.<unique>@example.com`) into the Email Address field. | The Name field displays the entered name and the Email Address field displays the entered email address. |
| 3 | Click the `Signup` button. | The signup step 2 page is displayed and its page title/heading text is `Enter Account Information`. |

### Notes

Source: PRD v0.1 §3 FR-ACC-01 AC 1, with the verbatim texts from §4 asserted in the same case; guest role context from §2 is captured as a precondition. The PRD states no field format, length, uniqueness-error or required-field rules, so no negative, validation or boundary case is derived — those behaviours are recorded as open questions instead.

## Open Questions

- If the Email Address entered is already registered, what should happen on clicking `Signup` (stays on /login? navigates? which exact error text is shown)? This is outside AC 1 but is the most likely real-user path.
- Are Name and Email Address required for `Signup`? If either is left empty, what exact validation message is displayed and is the button disabled or does submission fail?
- What email format rules apply (must contain `@` and a domain, allowed characters, max length) and what exact message is shown for an invalid format?
- Is the registered-email uniqueness check case-sensitive and does it trim leading/trailing whitespace (e.g. `QA@Example.com` vs `qa@example.com`)?
- Is there a minimum/maximum length for the Name field, and are numeric or special characters accepted?
- Can step 1 be submitted by pressing Enter in either field, or only by clicking the `Signup` button?
- What is the URL of the `Enter Account Information` page that the user should land on after `Signup`, so the step-1→step-2 handoff can be asserted on URL as well as on heading text?
- If a signed-in user navigates to /login directly, should they be redirected, and to where?
