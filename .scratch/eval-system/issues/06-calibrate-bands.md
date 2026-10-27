# 06: Calibrate the bands

**What to build:** Choose `pass_min` and `needs_review_min` from the labeled dev set and record the
trade-off between false PASS and false flag. Update the defaults only after the chosen pair is
confirmed on the held-out test set.

**Blocked by:** 05.

**Status:** ready-for-agent

- [ ] A sweep over candidate thresholds on dev, with TPR/TNR/false PASS at each
- [ ] The chosen pair and its rationale are recorded
- [ ] The test set is evaluated once at the chosen bands
- [ ] Defaults and the bands version are updated; old results remain interpretable
- [ ] No tuning after the test result is seen

## Decisions / assumptions

- The current 0.8 / 0.5 pair is a default, not evidence.
- A band change is a question-set-level decision: it changes every verdict and must be versioned.
- The goal is to make false PASS explicit, not to maximize a single number.
