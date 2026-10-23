# 22b: Required case metadata and requirement coverage

**What to build:** Extend the deterministic structure layer with checks that need case metadata and
a requirement model: required `priority`/`test_type`/`severity`, requirement-to-case coverage, and a
happy-path case per requirement. This slice decides how much of that is checked against the PRD and
how much is computed from the Test Case's declared `requirement_ids`.

**Shape:** likely extends `ReviewCase` with `priority`, `test_type`, and `severity` read from the
Test Case metadata, and adds coverage outcomes to `VerificationResult.structure`. Any rule change
bumps `CHECK_SET_VERSION`.

**Blocked by:** 22a (record shape and structure checks); the decisions below.

**Status:** ready-for-human

- [ ] Required case metadata is checked as a deterministic outcome
- [ ] Requirement-to-case coverage is computed from the Test Case's declared `requirement_ids`
- [ ] A happy-path case is required for each covered requirement
- [ ] The definition of "happy path" is explicit and tested
- [ ] The PRD requirement-ID policy is decided (see below) or the PRD-existence check is deferred
- [ ] Any rule change bumps `CHECK_SET_VERSION`
- [ ] Tests cover each failure and the clean case

## Decisions still open

1. **Coverage source:** use the Test Case's declared `requirement_ids` only, or compare against
   requirements parsed from the PRD text? The repo has no PRD parser by design (ADR-0005).
2. **PRD requirement IDs:** the spec allows IDs to be assigned when the PRD lacks them. A
   deterministic "ID exists in the PRD" check conflicts with that unless a PRD heading convention is
   introduced. Options: require a convention, drop the check, or defer it.
3. **Happy path:** which `test_type` values count? `Functional` and `Workflow`, or something else?
4. **Required metadata:** are `priority`, `test_type`, and `severity` all required, or only some?
5. **Parser shape:** extend `ReviewCase` with the metadata, or parse it separately in the structure
   module? Reusing the existing YAML block avoids a second parser.

## Out of scope

- The front-matter, duplicate-case, and non-empty-step checks from 22a.
- Automatability, locators, and live-app behaviour.
- Changing the Jev question set or bands.

## Comments

**2026-10-23 — split from 22.** The artifact-only checks shipped in 22a. This slice waits on the
coverage and PRD requirement-ID decisions; without them, a deterministic check would false-fail
auto-assigned requirement IDs.
