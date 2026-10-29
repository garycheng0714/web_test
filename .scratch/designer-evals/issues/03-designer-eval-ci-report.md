# 03: Report designer eval results in CI

**What to build:** A report-only CI job (manual + schedule, not every PR) that runs the
designer eval on the pinned PRD set and publishes the coverage report (and the semantic
judge report when ticket 02 exists) as a job summary and artifact. It must not block merges
or change `verify-test-case`.

**Blocked by:** 01 (coverage); 02 optional for semantic metrics.

**Status:** needs-triage

**Shape:**
- Boundary: workflow + job summary/artifact; no new production module.
- Invariants: report-only; no required check; fail soft on missing `OPENCODE_API_KEY` or
  model errors; pinned model.

## Tasks

- [ ] Add a workflow (`schedule` + `workflow_dispatch`) using `OPENCODE_API_KEY`.
- [ ] Run the eval; publish the report to the job summary and artifact.
- [ ] Fail soft with a clear message when the key is absent.
- [ ] Document the runbook and cost.
- [ ] Do not add it to required checks.

## Out of scope

- Gating the designer.
- Changing `verify-test-case`.
- Automation eval.
