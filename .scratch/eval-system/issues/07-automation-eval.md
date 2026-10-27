# 07: Add an automation eval

**What to build:** A local command that runs a fixed slice of test cases N times for one variant,
writes one run record per attempt, and renders a paired comparison against a baseline. A variant
means the model id, the instruction digest, and the skill content digest; one knob changes between
variants.

**Shape:**

- `RunRecord` — Pydantic boundary, JSONL: `stage`, `dataset_id`, `dataset_version`, `case_id`,
  `run_index`, `variant` (`model`, `instructions_digest`, `skill_digest`), `status`, `metrics`,
  `cost`, `duration_s`, `artifacts`.
- Invariants: one row per attempt; `run_index >= 1`; variant digests non-empty; no secrets;
  append-only.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Three cases (smoke, contact-us, register-login full) × three runs per variant
- [ ] Each run uses a throwaway clone and does not publish
- [ ] Metrics: final green, first-pass green, repairs, quality findings by rule, cost, duration
- [ ] Flake is reported per case across repeats
- [ ] The report shows per-case paired deltas and an aggregate with n
- [ ] SUT failures are separated from agent failures
- [ ] Failures are listed, not only averaged

## Decisions / assumptions

- The variant digest is content-based, so an edited skill cannot hide behind an unchanged name.
- The first slice measures runnability and the quality gate, not step fidelity or mutation.
- A run is agent-only; publishing is out of scope, so no token or PR noise.
- Cost is optional when the provider price is unknown; the field stays absent rather than zero.

## Out of scope

- Mutation testing and a controllable SUT.
- Step fidelity and per-step assertions.
