# 07: Gate

**What to build:** The human approval gate as a state on the test-case artifact plus a reusable
check. Approval is expressed by editing the artifact's front-matter `approval` line (no separate
command).

**Blocked by:** 05

**Status:** wontfix

- [x] The test-case document carries an explicit approval state with defined values (`draft` → `approved`)
- [x] A pure function reports whether the document is approved
- [x] The function's behavior is unit-tested for both states
- [x] Approval by editing the state line is documented

## Comments

**Superseded (wontfix).** The gate is no longer a front-matter `approval` state on a single
document. It is now the **merge** of the PR that adds a `test-case/<id>.md` file; the automation
workflow runs on that merge (agent-in-ci ticket 06). Approval by editing a file line gives way to
the GitHub review/merge. See ADR-0006, which supersedes ADR-0002's gate medium.

`is_approved` / `ApprovedDocumentError` (`web_test/planning/document.py`) remain only until the
`plan` rewrite (ticket 06) replaces the single qa-table document; they are not part of the new gate.
