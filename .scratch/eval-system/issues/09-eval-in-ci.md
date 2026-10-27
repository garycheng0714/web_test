# 09: Run the eval in CI and keep history

**What to build:** A workflow that runs the eval suites that exist (verifier validation, automation,
designer) on demand or on a schedule, uploads the report, and keeps a baseline so two runs can be
compared later. It is not a required PR check.

**Blocked by:** 05, 07, 08.

**Status:** ready-for-agent

- [ ] `workflow_dispatch` runs the suites; a schedule is optional
- [ ] The report and run records are uploaded as artifacts with a retention period
- [ ] A documented baseline location lets the next run compare against it
- [ ] A failed pre-registered criterion fails the job
- [ ] No new secrets beyond the existing model and Jev keys
- [ ] The workflow passes actionlint

## Decisions / assumptions

- Not every PR: the automation suite costs model calls and wall time.
- The baseline is a named artifact or path, not "latest"; a run must say what it compared against.
- The job is allowed to be manual until the suites are stable.

## Out of scope

- Per-PR gating.
- Dashboards.
- Automatic baseline promotion.
