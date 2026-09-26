# 10: Self-heal, fixme, and run report

**What to build:** The automator recovers from first-pass test failures within a bound, and
reports honestly on what it could not automate.

**Blocked by:** 08

**Status:** ready-for-agent

- [ ] On a failing run, the automator diagnoses and repairs, in a loop bounded to three attempts
- [ ] Repair may adjust tests and page objects
- [ ] A case that cannot be automated becomes a visible fixme with a reason, never a silent skip
- [ ] The final report lists generated files, per-test pass/fail, and any fixme'd cases
- [ ] Tests inject a model that first fails then succeeds, asserting the repair loop runs and is bounded
