# Coding-agent optimization runs — grounding, failure output, account fixtures

Experiments run on 2026-10-19 against `web_test/automation/coding_agent.py`, using the repository's
real SUT (`automationexercise.com`). The goal was to find cheap levers for output quality, wall-clock,
and token cost after the model choice was settled in [model-runs.md](model-runs.md).

**Status:** F (known SUT traps), C (`--tb=short`), and rule 19 (step fidelity) are in the source at
`670a59e`. B (lower snapshot budget) and D (text page inventory) were rejected. G (shared account
fixtures) is a quality win but a cost regression; the next experiment is a pre-built fixture scaffold
(G2).

## Non-levers

These were considered and did not earn a change:

- **Screenshots / image input.** A probe showed both `kimi-k2.7-code` and `deepseek-v4.1-flash`
  accept a 1280×720 PNG, at roughly 0.6–1.2k prompt tokens per image (kimi ~1.2k, deepseek ~0.6–1.2k
  depending on the request); prompt caching can make repeat sends cheaper. But an image carries no
  `aria-ref`, role, accessible name, or uniqueness information, so it cannot replace a live
  `snapshot()` for locators. It only helps visual/layout questions, which these functional cases do
  not test. The full pipeline was not run with images; this is a cost/grounding judgment, not a
  green/red A/B.
- **Static prompt dedupe.** `INSTRUCTIONS` and the house skill overlap, but cache hit rates were
  93–98% and new input was ~20–76k tokens per run. Deduping saves at most a few hundred tokens once,
  with regression risk; not worth it.
- **Lower snapshot budget (B).** Covered below: `max_content_tokens=2000` caused a missed upload
  input and a repair. Keep the 4000 default.
- **The real cost is request count and repair loops, not token volume.** Cache makes total input look
  large while new input stays small; wall-clock is driven by 22–87 model turns and 2–4 pytest runs
  per run.

## Method

- Model: `openai-chat:kimi-k2.7-code`; `WEB_TEST_REPAIR_ATTEMPTS=4`.
- Every run: fresh clone of the repo as the **workspace**, `uv sync --locked`, Chromium installed.
  The agent was invoked directly (`build_automation_agent` + `run_sync`), not through the publishing
  entrypoint, so no PR was opened.
- `WEB_TEST_USAGE=1 WEB_TEST_TRACE=1` captured `RunUsage` and the tool-call trace.
- Between variants the workspace was reset with `git reset --hard HEAD && git clean -fd`; one
  variable was changed at a time.
- The full suite was run separately after each agent run where noted. Generated tests add to the
  suite, so counts differ from the source-only `103 passed, 1 skipped`.
- Single run per variant. The SUT flakes and the model is nondeterministic; treat the cost deltas as
  directional, not statistically robust. The structural differences (fixtures vs no fixtures,
  nav step vs direct URL) are the reliable part.

## 1. Smoke baseline — `test-case-register-login-smoke.md` (1 case)

| Metric | Value |
| --- | --- |
| Green | yes |
| Requests | 22 |
| Tool calls | 30 |
| Input tokens | 379,087 (cache read 352,768; ~26,319 new) |
| Output tokens | 5,310 (reasoning 3,385) |
| Pytest runs | 2 |
| Elapsed | 130.1s |
| Full suite in clone | 104 passed, 1 skipped |
| Generated | `pages/login_page.py`, `pages/signup_page.py`, `tests/test_register_login_smoke.py`; `tests/conftest.py` edited |

Observations: 93% cache hit; only 2 `snapshot` calls and 5 `execute_js` calls. The simple page does
not exercise the snapshot budget. No repair. This made B look unattractive before the harder case
was run.

## 2. F / B / C — `test-case-0001.md` (Contact Us, 1 hard case)

The case has the documented traps: file upload, native confirm dialog, and a hidden duplicate success
node.

| Variant | Green | Requests | Tool calls | Input tokens (cache) | Output (reason) | Pytest runs | Elapsed | `execute_js` | `snapshot` | Full suite |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Control | yes | 29 | 37 | 516,946 (487,936) | 5,658 (3,271) | 2 | 191.5s | 12 | 2 | not separately run; target + subset green |
| **F** known SUT traps | yes | **25** | 35 | 425,110 (406,016) | 4,915 (2,576) | 1 | **119.5s** | **7** | 2 | 104 passed, 1 skipped |
| **B** `max_content_tokens=2000` + targeted reads | yes, after 1 repair | 30 | 37 | 518,811 (495,872) | 4,754 (2,156) | 3 | 170.0s | 5 | 2 | 104 passed, 1 skipped |
| **C** `--tb=short` | yes | 26 | 32 | 400,524 (382,208) | 4,459 (1,783) | 1 | 127.6s | 8 | 1 | 104 passed, 1 skipped |

What happened:

- **F:** adding `automationexercise.com` traps to the house skill (visible
  `.status.alert.alert-success`, hidden `.alert-success.alert`; Products PUA; ads already blocked)
  removed the DOM hunt for the success node. `execute_js` fell 12→7 and requests 29→25.
  Caveat: control ran an extra subset, while F only ran the target file; the ~7s subset does not
  explain the 72s gap, but the comparison is not perfectly apples-to-apples.
- **B:** lowering the tool-result budget to 2000 tokens appears to have truncated the upload input
  from the first `/contact_us` snapshot. The agent submitted the form, then discovered the input,
  failed once, and repaired. Snapshot volume is not the bottleneck; keep 4000.
- **C:** the command in the trace was
  `uv run pytest tests/test_contact_us.py -q --tb=short`, but the run was green, so there was no
  failure output to shorten. C is safe and only changes red-run verbosity.
- **Step fidelity:** C's generated test opened `/contact_us` directly instead of going Home → click
  Contact Us. The case's step 4 was skipped. This motivated rule 19 in the skill; it is not a C
  effect.

## 3. G / D — 4-case register-login slice (Cases 1, 2, 4, 7)

The slice keeps the account dependency chain: signup step 1 → create account → login → delete. It
was extracted into a temporary `register-login-slice.md` (112 lines) and passed to the agent; it was
not added to the repository. `request_limit` was raised from 50 to 120 for this slice.

| Variant | Green | Requests | Tool calls | Input tokens (cache) | Output (reason) | Pytest runs | Elapsed | Full suite | Account handling |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Control | yes | 46 | 63 | 1,729,003 (1,657,088) | 19,305 (12,756) | 4 | 435.3s | not separately run; target 4 passed, subset 3 passed / 1 skipped | test-file `_register_user` helper; 2 accounts left on the SUT |
| **G** fixtures | yes | 73 | 81 | 2,905,461 (2,829,056) | 20,925 (12,911) | 4 | **568.5s** | **107 passed, 1 skipped** | `registered_account` / `logged_in_account` fixtures with teardown |
| **D** page inventory | yes | **87** | **91** | 3,947,461 (3,870,976) | 18,099 (9,427) | 3 | 538.8s | **107 passed, 1 skipped** | test-file helpers; 2 accounts left on the SUT |

What happened:

- **G:** the agent built the two fixtures in `tests/conftest.py`, used them for Cases 4 and 7, logged
  out in `registered_account`, deleted in both teardowns, and kept Cases 1/2 as real signup tests.
  The first target run had 1 pass / 2 errors / 1 fail; it repaired and then passed. Quality win
  (order-independent, no account leaks, cleanup), but **+27 requests and +133s** vs control.
  Caveat: the teardowns catch all exceptions, so a failed cleanup would be silent.
- **D:** the skill inventory listed page URLs, headings, fields, and `data-qa` attributes, but did not
  replace grounding. The agent still used 5 `snapshot`, 4 `navigate`, and many `execute_js` calls;
  it also hit one click timeout and repaired. It produced no fixtures and left the same two accounts
  behind. **Rejected.**
- **Cache:** the slice runs kept 95–98% cache hits; new input was control ~71.9k, G ~76.4k, D ~76.5k
  tokens. The cost differences are mostly request count and wall-clock (each request re-reads the
  cached prefix), not new prompt content.

## 4. Batching — 1 case vs 3–4 cases

The one-case comparison uses the 0001 control; the four-case comparison uses the slice control. They
are not a controlled pair: the slice's extra cases are heavier (signup, date of birth, address,
login, delete) and the slice run had a repair, so the deltas are directional.

| Metric | 1 case (`test-case-0001` control) | 4-case slice control | Ratio |
| --- | ---: | ---: | ---: |
| Requests | 29 | 46 | 1.6× |
| Tool calls | 37 | 63 | 1.7× |
| Elapsed | 191.5s | 435.3s | 2.3× |
| Input tokens | 516,946 | 1,729,003 | 3.3× |
| New input (input − cache) | 29,010 | 71,915 | 2.5× |
| Output tokens | 5,658 | 19,305 | 3.4× |
| Pytest runs | 2 | 4 | 2× |
| Generated | 1 page, 1 test | 4 pages, 4 tests, header/conftest edits | — |

What is shared (the upside of batching):

- Skill loading, repo reading, conventions, and the PR body are done once.
- Page objects are reused across cases: login/signup/account pages are built once for four tests.
- A coherent user journey (signup → create → login → delete) exposes the real shared flow and the
  components worth extracting.

What grows (the downside of batching):

- **Context:** each request resends a longer history, so total input grows faster than the request
  count (3.3× vs 1.6×). Cache keeps the price down, but wall-clock still follows the request count.
- **Repair blast radius:** one failing test can lead to edits in a shared page object or
  `tests/conftest.py`, fixing one case while risking another. The 4-case control had one repair
  round with four failures; the 1-case control had none.
- **State and order:** multi-case runs expose account creation, logout, delete, and cleanup issues.
  The one-case smoke cannot show this; the 4-case control left two accounts on the SUT, which is what
  made G worth testing.
- **Step fidelity and case mixing:** more cases increase the chance of merging flows or skipping a
  step (the C run skipped Home → Contact Us).
- **Request limit:** one case fits comfortably under the default 50. The 4-case control reached 46;
  the G variant reached 73 and crossed the limit. Assume the 7-case artifact needs a higher
  `request_limit` or splitting.
- **Review and diagnosis:** one PR grows from one test to four tests plus multiple page objects, so
  the diff is larger and a failure is less localized.

Practical boundary:

- **1 case** — prompt, grounding, and single-page quality experiments; cheapest clear signal.
- **3–4 cases** — page-object reuse, account fixtures, state isolation, and request scaling. Pick a
  dependency chain (signup → create → login → delete) rather than unrelated cases.
- **7 cases** — acceptance: request limit, cleanup order, and final cost.

Rough incremental cost from this sample: about **5–9 requests and ~80 seconds per additional case**,
with state/repair risk rising. The confound is real: the slice's cases are heavier than Contact Us
and include one repair, so treat the slope as an order-of-magnitude estimate, not a benchmark.

## Decisions

| Change | Decision | Reason |
| --- | --- | --- |
| F known SUT traps | **Adopted** in `670a59e` | cheapest quality lever; removed success-node probing |
| C `--tb=short` | **Adopted** in `670a59e` | safe; only affects red runs; no green-run cost |
| Rule 19 step fidelity | **Adopted** in `670a59e` | C run skipped Home → Contact Us |
| B lower `max_content_tokens` | **Rejected** | 2000 caused a missed upload input and a repair; keep 4000 |
| D text page inventory | **Rejected** | no grounding reduction; +89% requests; no cleanup |
| G shared account fixtures | **Deferred to G2** | quality win, but the agent spent +58% requests building fixtures |

### Next: G2

Pre-build the account fixtures and the login/signup page objects in the repository, then have the
agent consume them instead of building them per run. The target shape is the G output
(`registered_account`, `logged_in_account`) with a teardown that does not swallow cleanup failures.
Use the site's API for setup/teardown only after verifying the endpoints. Measure against the same
4-case slice and the same metrics.

## Reproduction

Prepare a harness clone (the code under test) and a separate workspace clone (the repo the agent
edits):

```bash
tmp=$(mktemp -d)
git clone /path/to/web_test "$tmp/harness"
git clone /path/to/web_test "$tmp/ws"
(cd "$tmp/harness" && uv sync --locked)
(cd "$tmp/ws" && uv sync --locked && uv run playwright install chromium)
```

Measurement script (`$tmp/baseline.py`):

```python
import sys
import time
from pathlib import Path

from pydantic_ai.usage import UsageLimits

from web_test._run import run_sync
from web_test.automation.coding_agent import build_automation_agent
from web_test.automation.repair_guard import AutomationDeps, RepairBudgetExceeded
from web_test.model import resolve_model
from web_test.observability import configure_observability, log_trace

workspace = Path(sys.argv[1])
case = Path(sys.argv[2]).read_text(encoding="utf-8")

configure_observability()
agent = build_automation_agent(resolve_model(), workspace_dir=workspace)
deps = AutomationDeps()
start = time.perf_counter()
try:
    result = run_sync(
        agent.run(case, deps=deps, usage_limits=UsageLimits(request_limit=120))
    )
except RepairBudgetExceeded as exc:
    print(f"RED repair_budget_exceeded: {exc}", flush=True)
    print(f"PYTEST_RUNS={deps.pytest_runs}", flush=True)
    raise SystemExit(2)
except Exception as exc:
    print(f"ERROR {type(exc).__name__}: {exc}", flush=True)
    print(f"PYTEST_RUNS={deps.pytest_runs}", flush=True)
    raise

print(f"GREEN={result.output.pr_body is not None} ELAPSED={time.perf_counter() - start:.1f}s")
print(f"PYTEST_RUNS={deps.pytest_runs}")
print(f"USAGE={result.usage!r}")
log_trace(result)
```

Run from the harness clone:

```bash
cd "$tmp/harness"
PYTHONPATH="$tmp/harness" \
WEB_TEST_MODEL=openai-chat:kimi-k2.7-code \
WEB_TEST_REPAIR_ATTEMPTS=4 \
WEB_TEST_USAGE=1 WEB_TEST_TRACE=1 \
uv run python "$tmp/baseline.py" "$tmp/ws" test-case/test-case-0001.md
```

- Use `request_limit=50` for the smoke / single-case runs and `120` for the 4-case slice; record any
  limit hit instead of silently raising it.
- Reset the workspace between variants:
  `git -C "$tmp/ws" reset --hard HEAD && git -C "$tmp/ws" clean -fd`.
- Logs from this session are in
  `/var/folders/1s/brk6m17j3fvdqydj20rttdnm0000gn/T/opencode/web-test-slice-20261019/logs/` and the
  0001/smoke equivalents. They are temporary and not committed.

## Limitations

- One run per variant; the SUT is flaky and the model's step/verification choices vary. The agent
  sometimes ran only the target file, sometimes a subset, sometimes the full suite, which affects
  elapsed time and tokens.
- `kimi-k2.7-code` is not in pydantic-ai's price table, so the runs have token counts but no dollar
  cost. Cache-read pricing is provider-specific.
- The slice is a temporary artifact derived from `test-case-register-login.md`; the source case file
  remains untracked. The generated page objects and tests lived only in the temporary workspace
  clones.
