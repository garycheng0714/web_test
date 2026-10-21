# Review eval fixtures

These are golden regression datasets for the Jev verifier, not production ground truth. They
answer whether a change to the question set, bands, or model makes the verifier worse.

## register_login_golden_v1.json

- Pinned PRD: the `prd` field embeds the `register-login` PRD used by the experiment.
- Good cases: `G1`, `G2`.
- Bad cases: `B1`–`B4`, each with the check that should catch it.
- `expected_failures` lists the expected failing dimension, not exact probabilities.
- Each case carries `preconditions`; the `continuity` question reads them.
- `kill_criteria` is pre-registered; do not loosen it after seeing the result.

Run:

```bash
uv run python -m web_test.planning.review.eval \
  --fixtures tests/fixtures/review_eval/register_login_golden_v1.json
```

## Update rules

- Changing cases, the PRD, expected failures, or kill criteria means a new dataset version.
- Keep old versions; they are regression baselines.
- A failing kill criterion is a finding, not a reason to edit the fixture.
- v1 was revised in place when step `complete` was replaced by `continuity`: B4's expected dimension
  was renamed, and each case gained the preconditions the new question reads. Step-level `complete`
  false-flagged good cases; see ticket 26.

## Limits

- One PRD, six cases, and synthetic bad variants.
- One run is directional; it is not statistical confidence.
- The dataset does not replace the human Gate or production review.
