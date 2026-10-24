# 17: Fail the automate job on a red outcome

**What to build:** An `AGENT_RED` or `SUITE_RED` run currently exits 0, so the Actions run is green
and nobody notices unless they open it. Make those two outcomes exit 1 so the run shows a red X and
GitHub's failure notification fires. The merge gate does not change: red still opens no branch and
no PR. Split out of ticket 07, which chose the green-job contract and left this as a follow-up.

**Blocked by:** 07 (done; live-verified).

**Status:** ready-for-agent

**Shape:**

- `entrypoint.main()` exit codes: `PUBLISHED` 0, `NO_CHANGES` 0, `AGENT_RED` 1, `SUITE_RED` 1,
  `FAILED` 1.
- Invariant: the step summary and the evidence files are written **before** the non-zero exit.
- Invariant: the gate is unchanged; a red outcome still publishes nothing.
- `.github/workflows/automate.yml` is unchanged; its `if: always()` upload still runs after the failed
  step. Artifact survival on a job timeout is out of scope.

- [ ] `AGENT_RED` and `SUITE_RED` make `main()` exit 1; `PUBLISHED` and `NO_CHANGES` stay 0;
      `FAILED` stays 1
- [ ] The summary and evidence are written before the exit
- [ ] Unit-tested: the exit-code mapping for all five statuses
- [ ] `automate.yml` still uploads the artifact after the failed step
- [ ] README says a red run fails the job
- [ ] Verified live on a red run: job red, artifact still uploaded

## Notes

`NO_CHANGES` stays green on purpose: the agent producing nothing allowed is not by itself a red
outcome, and failing it would add noise. If it should page too, decide that separately.
