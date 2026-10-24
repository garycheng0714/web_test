# 10: Self-heal, fixme, and run report

**What to build:** The automator recovers from first-pass test failures within a bound, and
reports honestly on what it could not automate.

**Blocked by:** None (superseded by 10a/10b; the repair loop is already implemented).

**Status:** wontfix

**Superseded.** The bounded repair loop already exists in `web_test/automation/repair_guard.py`.
The remaining work is split into 10a (generated-test quality gate) and 10b (run report). Fixme/skip
reasons are deferred and have no ticket.

- [ ] On a failing run, the automator diagnoses and repairs, in a loop bounded to three attempts
- [ ] Repair may adjust tests and page objects
- [ ] A case that cannot be automated becomes a visible fixme with a reason, never a silent skip
- [ ] The final report lists generated files, per-test pass/fail, and any fixme'd cases
- [ ] Tests inject a model that first fails then succeeds, asserting the repair loop runs and is bounded

## Comments

**2026-10-24 — metadata.** The old blocker 08 is wontfix/superseded. The bounded repair loop exists (`repair_guard.py`); fixme markers and the run report do not. Re-scope before implementation.

**2026-10-24 — split and superseded.** 10a covers the generated-test quality gate; 10b covers the
run report. This ticket stays `wontfix` for the rest. Fixme/skip-reason markers are not planned.
