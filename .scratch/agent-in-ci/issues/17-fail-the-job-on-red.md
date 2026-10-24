# 17: Fail the automate job on a red outcome

**What to build:** An `AGENT_RED` or `SUITE_RED` run currently exits 0, so the Actions run is green
and nobody notices unless they open it. Make those two outcomes exit 1 so the run shows a red X and
GitHub's failure notification fires. The merge gate does not change: red still opens no branch and
no PR. Split out of ticket 07, which chose the green-job contract and left this as a follow-up.

**Blocked by:** 07 (done; live-verified).

**Status:** ready-for-human (done; verified live)

**Shape:**

- `entrypoint.main()` exit codes: `PUBLISHED` 0, `NO_CHANGES` 0, `AGENT_RED` 1, `SUITE_RED` 1,
  `FAILED` 1.
- Invariant: the step summary and the evidence files are written **before** the non-zero exit.
- Invariant: the gate is unchanged; a red outcome still publishes nothing.
- `.github/workflows/automate.yml` is unchanged; its `if: always()` upload still runs after the failed
  step. Artifact survival on a job timeout is out of scope.

- [x] `AGENT_RED` and `SUITE_RED` make `main()` exit 1; `PUBLISHED` and `NO_CHANGES` stay 0;
      `FAILED` stays 1
- [x] The summary and evidence are written before the exit
- [x] Unit-tested: the exit-code mapping for all five statuses
- [x] `automate.yml` still uploads the artifact after the failed step
- [x] README says a red run fails the job
- [x] Verified live on a red run: job red, artifact still uploaded

## Notes

`NO_CHANGES` stays green on purpose: the agent producing nothing allowed is not by itself a red
outcome, and failing it would add noise. If it should page too, decide that separately.

**2026-10-24 — implemented and verified live.**

- PR #21 added `exit_code()`: `PUBLISHED`/`NO_CHANGES` return 0; `AGENT_RED`, `SUITE_RED`, and
  `FAILED` return 1. The summary and evidence are written before the exit; `automate.yml` is
  unchanged and its `if: always()` upload still runs.
- Live red run: merged PR #22 (throwaway deliberately-wrong case) with `WEB_TEST_REPAIR_ATTEMPTS=2`;
  `automate` run `40055442740` ended **failure**. Step 8 "Implement the tests and open a PR" failed,
  step 9 "Upload automation evidence" still succeeded, and artifact
  `automation-evidence-40055442740-1` contained `summary.md` (`agent_red`), the failing
  `pytest-output.txt`, `trace.txt`, and `suite-output.txt` ("the suite was not run"). No automation
  branch or PR was opened.
- Caveat: that run reported `Generated files: none` because the agent deleted its own files
  (`rm tests/test_live_evidence_red.py`, `rm pages/login_page.py`) before returning; the trace keeps
  the commands, but the evidence cannot copy files that no longer exist.
- The cleanup PR on `chore/remove-live-evidence-red-2` removes the fixture and teaches `automate.yml`
  to skip a merged PR that only **removes** test-case files; the previous cleanup merge (#19) had
  triggered a failing `automate` run (`40053017116`) for exactly that reason.
