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

Include only relevant cases; do not add irrelevant generic tests.

- Core functional: happy-path create/save/submit; view, edit, delete, cancel, reset, clear,
  retry; required vs optional fields; field dependencies; calculations, defaults, uniqueness;
  duplicate handling; success/warning/validation/error messages; confirmation popups; persistence
  after save, refresh, logout/login, close/reopen, and navigation away/back.
- UI and interaction: labels, placeholders, help text, icons, buttons, links, tabs, menus, table
  headers; required indicators; disabled/enabled states; search, filter, sort, pagination, empty
  and no-result states; loading states; repeated submit clicks.
- Workflow and business rules: status transitions and invalid transitions; approval, rejection,
  return, assignment, cancellation; role- and permission-based access; view-only behavior;
  dependencies between records, modules, fields, or prior cases.
- Data and integration: backend/API validation when UI validation can be bypassed; formatting in
  lists, details, exports, downloads; import/export and attachment handling; notifications or
  downstream updates when relevant.
- Negative and risk: invalid, missing, duplicate, expired, unauthorized, too-large, too-small,
  malformed, unsupported, and conflicting inputs; direct URL/API permission attempts; race
  conditions from double submission or concurrent edits; recovery from validation errors without
  losing entered data.

## Boundary and Edge Cases

Include boundaries that are logically relevant even when not explicitly stated, but document
assumptions.

- Text fields: empty required value; whitespace only; leading/trailing spaces; min-1, min, max,
  max+1 length; special characters; Unicode; very long pasted text; duplicates and case
  sensitivity.
- Numeric fields: empty, zero, negative, decimal, very large, non-numeric, scientific notation,
  comma-formatted; min-1, min, max, max+1; precision and rounding.
- Date/time: empty required date; invalid format; start after end; same start/end; past, current,
  future; leap day; month/year boundary; timezone-sensitive; expired dates.
- Dropdowns/multi-selects: no selection, valid, all, max+1, duplicate, disabled option, dependent
  changes, parent changed after child set.
- File uploads: no file, supported/unsupported type, empty, max size, above max, multiple files,
  duplicate names, special characters, corrupted; preview, remove, replace, download, persistence.
- Search/filter/sort/pagination: exact/partial/case/special-character/no-result; single, multiple,
  invalid combination, reset; ascending/descending, sorting with empty values; page boundaries,
  page-size change, no records.
- Workflow/permissions: unauthorized role, read-only role, owner vs non-owner, approver vs
  requester, inactive user; valid/invalid/skipped transitions; direct URL/API access.
- Rare user behavior: double-click submit; navigate away with unsaved changes; refresh during
  entry; back after submit; concurrent edit; session timeout during save/approval.

## Deduplication

Apply before finalizing.

- Treat cases as duplicates when they share feature/module, role or permission context,
  preconditions, action under test, input category, and expected result. Different wording alone
  does not justify a separate case.
- Merge cases that test the same behavior and differ only by minor examples; list the
  representative values on the relevant step.
- Keep cases separate when role, permission, ownership, status/workflow stage, validation rule or
  boundary, error message or expected behavior, risk/severity, UI vs backend behavior, or
  save/submit/delete outcome changes meaningfully.
- Each final case must have one clear purpose, be traceable, be executable by a manual QA engineer
  without hidden knowledge, and have a specific, observable expected result.

## Output

Return only the test cases, as a list. Each case records:

- `requirement_ids`: the requirement id(s) it covers.
- `module_feature`, `test_scenario`, `preconditions`, `notes`.
- `steps`: a list where each step is an `action` with its own `expected_result`.
- `priority`: `High`, `Medium`, or `Low`.
- `severity`: `Critical`, `Major`, `Minor`, or `Trivial`.
- `test_type`: one of `Functional`, `Negative`, `Boundary`, `Validation`, `UI`, `Permission`,
  `Workflow`, `Integration`, `Regression`, `Usability`, `DataPersistence`.

Put prerequisites in `preconditions`, not the first step. Use `notes` for source or assumptions when
a case is inferred rather than stated.
