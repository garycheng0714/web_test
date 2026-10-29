# Designer eval report: register-login-20261029T070829Z

- PRD: `register-login.md`
- Model: `openai-chat:deepseek-v4.1-flash`
- Requirements: 6
- Claims: 7
- HUMAN labels: 7

## Coverage

- Covered: 6 / 6 (100%)
- Wilson 95% CI: [0.61, 1.00]
- Not covered: 0
- Missing: 0
- Unlabeled: 0

## Requirements

| Requirement | Cases | Human labels | Status |
| --- | --- | --- | --- |
| FR-ACC-01 | case-1 | pass(local) | `covered` |
| FR-ACC-02 | case-2 | pass(local) | `covered` |
| FR-ACC-03 | case-3 | pass(local) | `covered` |
| FR-ACC-04 | case-4, case-5 | pass(local), pass(local) | `covered` |
| FR-ACC-05 | case-6 | pass(local) | `covered` |
| FR-ACC-06 | case-7 | pass(local) | `covered` |

## False tags

None.

## Code checks

- Invented IDs: 0
- Empty requirement_ids: 0
- Duplicate cases: 0
- Structure failures: 0

## Limits

- Small PRD sample; the Wilson CI is wide.
- Coverage treats unlabeled requirements as not covered; finish labeling before trusting the number.
- A case claiming multiple requirements produces multiple claim labels.
