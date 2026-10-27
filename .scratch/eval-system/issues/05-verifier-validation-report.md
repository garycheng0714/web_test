# 05: Report verifier validation metrics

**What to build:** A report that measures the verifier against the labeled set: TPR and TNR, false
PASS, false flag, the four-class confusion matrix, BLOCKED rate, and an interval for each rate.
Dev and test are reported separately; the test set runs once.

**Blocked by:** 04.

**Status:** ready-for-agent

- [ ] TPR/TNR use PASS as the positive class; NEEDS_REVIEW/FAIL/BLOCKED collapse to "not PASS" for TNR
- [ ] False PASS is reported on its own (human FAIL, verifier PASS)
- [ ] The confusion matrix includes BLOCKED
- [ ] Dev and test are separate; the test number is reported once and never used to tune
- [ ] Every rate carries n and a Wilson or bootstrap interval
- [ ] Per-dimension breakdown, with "inconclusive" when a dimension has no cases
- [ ] Tests cover the metrics, the split enforcement, and the single-test-run rule

## Decisions / assumptions

- The existing catch/false-flag report remains as the regression view; this is the validation view.
- A verifier that is better at TPR but much worse at TNR is not automatically an improvement.
- BLOCKED is not a catch and not a pass; it is reported separately.

## Out of scope

- Choosing the bands (06).
- Reporting cost.
