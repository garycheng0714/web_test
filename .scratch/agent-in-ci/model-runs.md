# Coding-agent model runs — sample case

Experiment log for choosing the coding agent's model. Every run used the **same sample case**
(`test-case/test-case-0001.md`, Contact Us Form) and the agent **alone** (no publish), via
`create_automation`, judged by `green = pr_body is not None`.

## instructions 版本圖例（依迭代順序）

- **v0** — ticket-04 instructions (`base_url` from front-matter; verify loop); skill without rules 14–18.
- **v1** — + Tests paragraph (`tmp_path`; post-interaction content by text/role) and the repair bound.
- **v2** — + read `pages/base_page.py`; (skill) rule 14 constructor.
- **v3** — + (skill) rule 15 file upload.
- **v4** — + (skill) rule 16 Playwright Python API vs browser tools.
- **v5** — + (skill) rule 17 unique locator (for actions too).
- **v6** — + (skill) rule 18 `networkidle`.

## Results

| Model | instructions | repair | cost | requests | tool_calls | green | Notes |
|---|---|---|---|---|---|---|---|
| `google:gemini-2.5-flash-lite` | v0 | — | — | — | — | ✗ | structured output failed (`Exceeded maximum output retries`); wrote nothing |
| `google:gemini-2.5-pro` | v0 | — | — | — | — | — | retired for new users (404) |
| `google:gemini-3.1-pro-preview` | v0 | 3 | n/a | n/a | n/a | ✓ | full pipeline run went green and **opened PR #1**; usage not captured |
| `google:gemini-2.5-flash` | v0 | — | $0.1034 | 32 | 28 | ✗ | 6 pytest runs, no convergence (one run commented out the assertion) |
| `google:gemini-2.5-flash` | v1 | 1 | $0.0536 | 18 | — | ✗ | repair bound tripped |
| `google:gemini-2.5-flash` | v2 | 1 | $0.0366 | 13 | — | ✗ | |
| `google:gemini-2.5-flash` | v3 | 1 | $0.0362 | 14 | — | ✗ | |
| `google:gemini-2.5-flash` | v4 | 1 | $0.0578 | 20 | — | ✗ | |
| `google:gemini-2.5-flash` | v5 | 1 | $0.0560 | 17 | — | ✗ | **commented out the success assertion** (gamed green) |
| `google:gemini-2.5-flash` | v6 | 10 | $0.0668 | 21 | 21 | ✓ | went green after 3 repairs / 4 pytest runs |
| `google:gemini-3.5-flash` | v1 | 1 | $0.1854 | 38 | 37 | ✗ | most requests |
| `google:gemini-3.6-flash` | v5 | 1 | $0.1599 | 34 | 33 | ✗ | test essentially correct; stuck on the ambiguous Home button / SUT flake |
| `google:gemini-3.8-flash` | v1 | 1 | — | >50 | — | ✗ | aborted at pydantic-ai `request_limit=50` |
| `openai-chat:kimi-k2.7-code` (new default) | v6 | 10 | n/a | 30 | 35 | ✓ | genuine output, passed 3/3 locally; `networkidle` inside `expect_loaded` |

## Caveats

- **Not apples-to-apples.** v1–v5 were measured *while the instructions/skill were being improved*;
  the versions are not comparable with each other across the cost/quality columns.
- v1–v5 cost/requests are taken from the session log (their run logs were deleted) and are
  **approximate**; the `kimi-k2.7-code` row has `kimi.log` on disk.
- All rows are **agent-only** except the pro run, which published and opened PR #1.
- `cost` comes from pydantic-ai's price table: `kimi-k2.7-code` is not in it (`n/a`), and the pro run
  did not set `WEB_TEST_USAGE`.
- The SUT (Contact Us) itself flakes — the success message is intermittently empty. The case is
  unusually hard: file upload + a native confirm dialog + a **hidden duplicate** success node.

## How to rerun

```bash
tmp=$(mktemp -d)
git clone /Users/garycheng/PycharmProjects/web_test "$tmp/ws"
(cd "$tmp/ws" && uv sync --locked)

# from the repo root:
WEB_TEST_MODEL=<model-id> WEB_TEST_USAGE=1 WEB_TEST_TRACE=1 WEB_TEST_REPAIR_ATTEMPTS=<n> \
uv run python -c "
from pathlib import Path
from web_test.automation.coding_agent import create_automation
text = Path('test-case/test-case-0001.md').read_text(encoding='utf-8')
r = create_automation(text, workspace_dir='$tmp/ws')
print('green:', r.pr_body is not None)
"
```

`WEB_TEST_USAGE` prints the run's usage to stderr; `WEB_TEST_TRACE` prints the tool-call sequence and
per-request usage. `WEB_TEST_MODEL` is optional (defaults to `resolve_model()`).

## Related

- [optimization-runs.md](optimization-runs.md) — F/B/C/G/D experiments, decisions, and the G2 next step.
