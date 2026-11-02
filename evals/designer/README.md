# Designer eval

Report-only eval for the PRD-to-test-case designer. It measures requirement coverage and
claim alignment in a local Phoenix instance. It is not a production gate and does not run in CI.

The contract lives in [`spec.md`](spec.md). Tickets and review records stay under
`.scratch/designer-evals/`.

## Run

Start Phoenix in one terminal:

```bash
uvx arize-phoenix serve
```

Run one designer eval in another:

```bash
PYTHONPATH=. uv run --group eval python evals/designer/run_eval.py \
  --prd prd/register-login.md
```

Annotate the claim spans in Phoenix, then export and report:

```bash
PYTHONPATH=. uv run --group eval python evals/designer/export_labels.py --run <run-id>
PYTHONPATH=. uv run --group eval python evals/designer/report.py --run <run-id>
```

`WEB_TEST_DESIGN_MODEL` pins the designer model. Each run costs one designer call.

## Judge

The semantic judge reads a committed dev set under `judge/data/` and writes judgements plus a
TPR/TNR report under `judge/runs/` (gitignored):

```bash
PYTHONPATH=. uv run --group eval python evals/designer/judge.py \
  --dataset automationexercise --source-run house-automationexercise-20261029 --limit 10
```

`WEB_TEST_JUDGE_MODEL` pins the judge model (default `openai-chat:kimi-k2.7-code`). The data is
one PRD only, so this is a dev set: do not publish TPR/TNR as a general estimate yet.

## Layout

```text
evals/designer/
├── run_eval.py          # designer -> Phoenix eval units
├── export_labels.py     # Phoenix annotations -> labels.jsonl
├── report.py            # labels + units -> report.md
├── judge.py             # judge -> JSONL + TPR/TNR report
├── designer_eval/       # parsing, units, annotations, artifacts, Phoenix I/O, judge
├── judge/data/          # committed dev set (PRD + labeled claims)
├── judge/runs/          # local judge output, gitignored
├── phoenix/             # local instrumentation probes
├── spec.md              # eval contract
└── runs/                # local run artifacts, gitignored
```

`runs/` is machine-local output. Do not commit it.

## Test

```bash
uv run pytest tests/designer_evals -q
```
