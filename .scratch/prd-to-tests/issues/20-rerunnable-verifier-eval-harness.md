# 20: Make the verifier eval rerunnable

**What to build:** One command that replays the known-good and known-bad Test Case variants through
the current review and reports, per check: caught or not caught, false flags on good cases, model
and question-set version, tokens, and elapsed time. Results are grouped under the v1 bands
(`PASS`, `NEEDS_REVIEW`, `FAIL`, `BLOCKED`) so the same run can inform the shadow-to-required
decision. The variants are the ones already used in the Jev experiments. The report states the
one-run and small-sample limits instead of presenting a directional result as stable.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Known-bad and known-good variants are checked in as fixtures
- [ ] One command runs the full set without hand-built request files
- [ ] The report shows per-check catch and false-flag counts under the v1 bands, model version,
      question-set version, tokens, and elapsed time
- [ ] Pre-registered kill criteria are part of the run output
- [ ] The report includes the `NEEDS_REVIEW` rate and override rate needed for the required-check
      decision
- [ ] A check with no discriminating variant is reported as inconclusive, not as passing
- [ ] The summary distinguishes one-run direction from a reproduced result
- [ ] Tests cover the catch/false-flag tally and the inconclusive case
