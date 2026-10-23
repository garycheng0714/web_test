# 20: Make the verifier eval rerunnable

**What to build:** One command that replays the known-good and known-bad Test Case variants through
the current review and reports, per check: caught or not caught, false flags on good cases, model
and question-set version. Results are grouped under the v1 bands
(`PASS`, `NEEDS_REVIEW`, `FAIL`, `BLOCKED`) so the same run can inform the shadow-to-required
decision. The variants are the ones already used in the Jev experiments. The report states the
one-run and small-sample limits instead of presenting a directional result as stable.

**Blocked by:** None (can start immediately).

**Status:** ready-for-human

- [x] Known-bad and known-good variants are checked in as fixtures
- [x] One command runs the full set without hand-built request files
- [x] The report shows per-check catch and false-flag counts under the v1 bands, model version,
      and question-set version
- [x] Pre-registered kill criteria are part of the run output
- [x] The report includes the `NEEDS_REVIEW` rate and override rate needed for the required-check
      decision
- [x] A check with no discriminating variant is reported as inconclusive, not as passing
- [x] The summary distinguishes one-run direction from a reproduced result
- [x] Tests cover the catch/false-flag tally and the inconclusive case

## Comments

**2026-10-21 — implemented.**

- Fixtures: `tests/fixtures/review_eval/register_login_golden_v1.json` (G1/G2 good, B1–B4 bad, expected failures,
  kill criteria).
- Harness: `web_test/planning/review/eval.py` (measurement and CLI), `eval_set.py` (fixture
  schema), `eval_report.py` (report and rendering); run with
  `uv run python -m web_test.planning.review.eval --fixtures tests/fixtures/review_eval/register_login_golden_v1.json`.
- Tests: `tests/planning/test_review_eval.py` (catch/hard-fail/false-flag tally, inconclusive
  dimension, override n/a, fixture loading).
- Decisions: `caught = FAIL + NEEDS_REVIEW`; `hard_fail` reported separately; `override_rate`
  is `n/a` until 24b.
- Live v3 run: caught 4/4, hard_fail 4/4, bad blocked 0, but **good false flags = 4** on the
  `complete` dimension (G1 step 3 p=0.51; G2 steps 1–3 p=0.54–0.71). Needs-review rate: 2/6 cases.
  Kill criteria reported **FAIL**.
- This is a real calibration finding: applying `complete` to every step false-flags good cases
  under the v1 bands. Tracked in ticket 26; do not turn 24b required until it is resolved.
- `uv run pytest`: 136 passed, 1 skipped.

**2026-10-21 — step `complete` replaced by `behavior`.** The fixture now carries `preconditions`;
B4's expected dimension is `behavior`. Re-run (3 runs, same verdicts): caught 4/4, hard_fail 4/4,
B4 `behavior` p=0.05, G2 false flags = 4 (AC alignment p=0.78–0.79; behavior steps 1–3
p=0.75–0.77). Kill criteria still **FAIL**. Details in ticket 26.

**2026-10-21 — step `complete` replaced by `continuity`.** `behavior` left 3 G2 false flags; the
refined `continuity` check (reachable from preconditions/earlier steps, values the action enters do
not need to pre-exist) passes the kill criteria. Final 3-run result (reproduced): caught 4/4,
hard_fail 4/4, B4 `continuity` p=0.13, G1/G2 zero false flags. Real artifact: 16/16 continuity,
`NEEDS_REVIEW` only from AC alignment (Case 2 p=0.75). See ticket 26.

### Flow

```text
fixtures
  ├─ PRD
  ├─ good cases
  ├─ bad cases（含預期哪個 check 該抓到）
  └─ kill criteria
        │
        ▼
建立 ReviewSubject
        │
        ▼
run_review_on(subject, test_case_text, system_one=...)
        │
        ▼
VerificationRecord
  ├─ per-check status（v1 bands）
  ├─ model
  ├─ question-set version
  └─ needs-review rate
        │
        ▼
逐項評分
  ├─ bad case：預期 check 是否 FAIL / NEEDS_REVIEW？
  ├─ good case：是否有任何非 PASS？（false flag）
  ├─ 每個 dimension 是否有 discriminating bad variant？
  └─ kill criteria 是否通過？
        │
        ▼
報表
  ├─ per-check catch / false flag
  ├─ inconclusive checks
  ├─ one-run vs reproduced
  └─ 是否足以支撐 24b 轉 required
```

- `caught = FAIL + NEEDS_REVIEW`；`hard_fail` 另外統計。
- `override_rate` 目前是 `n/a`，等 24b 的人工裁決實作。
- 沒有 bad variant 的 dimension 標成 `inconclusive`，不能算 pass。

**2026-10-21 — cost reporting removed.** The report no longer shows tokens or elapsed time. Measured
cost is low (about 12.5k input / 1.3k output tokens and 0.5 s per run) and was not an input to any
decision, while reading it forced the eval to keep a second Jev adapter that parsed the SDK's usage
payload. The report keeps model, question-set version, and the needs-review rate.

**2026-10-23 — tracker cleanup.** All acceptance items are checked; status moved to `ready-for-human`.
