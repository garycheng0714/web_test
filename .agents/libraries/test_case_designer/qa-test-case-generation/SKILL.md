---
name: qa-test-case-generation
description: Use when generating manual QA test cases from a PRD or requirements document; especially when coverage, deduplication, traceability, validations, permissions, workflows, or edge cases matter.
---

# QA Test Case Generation

Adapted from `saleem-daqa/qa-test-case-generation` (MIT). Trimmed for PRD-text input and
structured output; the coverage, boundary, and deduplication rules are inlined below.

## Overview

Act as a senior manual QA engineer. Read the requirements, then produce professional, complete,
practical, non-duplicated test cases that are traceable to requirements.

Do not invent unrealistic requirements; document assumptions and clarifications when information
is missing.

## Inputs

- Required: a PRD or requirements document, as markdown or plain text.
- Optional: existing test cases (for reuse or duplicate removal), roles, permissions, and
  business rules stated in the document.

## Workflow

### 1. Requirement Review

Extract and organize:

- Features, modules, screens, fields, actions, buttons, menus, links, uploads, and downloads.
- Workflows, alternate flows, approvals, rejections, cancellations, edits, deletes, and status
  transitions.
- Business rules, validations, calculations, dependencies, prerequisites, permissions, and roles.
- Required and optional fields, accepted formats, defaults, uniqueness, min/max lengths, numeric
  ranges, date rules, and file constraints.
- Search, filter, sort, pagination, reset, save/submit/cancel, refresh/reopen, persistence,
  duplicates, notifications, and messages.
- Track unclear or missing details in the affected case's `notes`; do not hide ambiguity inside
  test cases.

### 2. Test Case Design

Cover the feature from user intent through data persistence. Prefer `Verify that...` in scenarios
and expected results; avoid vague wording such as `works correctly`, `properly`, or `as expected`
unless followed by a specific verifiable behavior.

Use **Coverage**, **Boundary and edge**, and **Deduplication** (below) as the checklists.

### 3. Traceability

Every case must be traceable to the requirement id(s) it covers (`requirement_ids`). When the PRD
has no ids, reference the requirement text in `notes`.

## Coverage

Add only cases the PRD actually supports. Keep the suite small and dense — do not pad. For each
requirement:

1. **One happy-path case** (the primary success behavior).
2. **At most one** negative/validation case, only when the PRD states a validation rule.
3. **A boundary case only when the PRD states a limit or rule that the happy-path case does not
   already exercise.**

Do not derive cases from the PRD's grounding or observation notes: observed option sets, default
values, disabled/read-only fields, or unselected-by-default controls are for automation, not
requirements, and a happy-path case already exercises the controls it uses.

Anything the PRD leaves undefined or contradictory — validation messages, error recovery, field
formats, case-sensitivity, trimming, session persistence, permission redirects, race conditions,
timing — is **not** a case. Record it under `open_questions` instead. A case whose expected result is
a guess will fail against the real system.

## Boundary and Edge Cases

Include a boundary case **only** when the PRD states a limit or rule and the happy path does not cover
it. Do not invent boundaries, races, or rare-user behaviour, and do not turn observed UI details
(option sets, default values, disabled/read-only fields, unselected-by-default controls) into cases.
Put undefined behaviour under `open_questions`.

## Deduplication

Apply before finalizing.

- Treat cases as duplicates when they share feature/module, role or permission context,
  preconditions, action under test, input category, and expected result. Different wording alone
  does not justify a separate case.
- Merge cases that test the same behavior and differ only by minor examples; list the
  representative values on the relevant step.
- Do **not** add a case that merely restates others: an end-to-end re-run of several cases, a sweep
  asserting every message, or a header/role check whose assertions already appear in the individual
  cases. Fold such checks into the case that owns the behavior.
- Keep cases separate only when role, permission, ownership, status/workflow stage, validation rule
  or boundary, error message or expected behavior, risk/severity, UI vs backend behavior, or
  save/submit/delete outcome changes meaningfully.
- Each final case must have one clear purpose, be traceable, be executable by a manual QA engineer
  without hidden knowledge, and have a specific, observable expected result.

## Output

Return the test cases and the open questions.

Each case records:

- `requirement_ids`: the requirement id(s) it covers.
- `module_feature`, `test_scenario`, `preconditions`, `notes`.
- `steps`: a list where each step is an `action` with its own `expected_result`.
- `priority`: `High`, `Medium`, or `Low`.
- `severity`: `Critical`, `Major`, `Minor`, or `Trivial`.
- `test_type`: one of `Functional`, `Negative`, `Boundary`, `Validation`, `UI`, `Permission`,
  `Workflow`, `Integration`, `Regression`, `Usability`, `DataPersistence`.

`open_questions`: the behaviours the PRD leaves undefined or contradictory, each phrased as a question
for the product owner. An open question must be about the **product's behaviour** — never about test
data, the test environment, or the test process (e.g. where a fixture account comes from). Never turn
an open question into a case.

Put prerequisites in `preconditions`, not the first step. Use `notes` for the source of a case.
