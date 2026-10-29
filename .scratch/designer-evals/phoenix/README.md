# Designer + Phoenix spike

Throwaway spike: send one designer run to a local Phoenix instance. This does not touch
`web_test/planning/designer.py` or the ticket 01 evaluator.

Background on Phoenix itself: `learn/evals/reference/phoenix.md`.

## Run

Terminal A:

```bash
uvx arize-phoenix serve
```

Terminal B:

```bash
cd /Users/garycheng/PycharmProjects/web_test
PYTHONPATH=. uv run --with openinference-instrumentation-pydantic-ai \
  python .scratch/designer-evals/phoenix/spike.py
```

Open `http://127.0.0.1:6006` -> project `web-test-designer`.

Options:

```bash
python .scratch/designer-evals/phoenix/spike.py --prd prd/login-smoke.md
python .scratch/designer-evals/phoenix/spike.py --instrumentation-version 2
```

## What to expect

One trace with four spans:

```text
invoke_agent test_case_designer     AGENT
  ├─ chat deepseek-v4.1-flash       LLM
  ├─ execute_tool load_capability   TOOL
  └─ chat deepseek-v4.1-flash       LLM
```

The agent span has the PRD as `input.value` and `DesignOutput` as `output.value`. The chat
spans carry messages, tool definitions, finish reason, and token counts.

## Findings (2026-10-29)

- `openinference-instrumentation-pydantic-ai==0.1.30` works with `pydantic-ai==2.54.0` on
  Python 3.13.
- `InstrumentationSettings(version=5)` maps cleanly; span names are `invoke_agent` /
  `execute_tool`.
- `version=2` also mapped, but Pydantic AI deprecates versions 2–4. Use 5.
- `Agent.instrument_all(...)` is enough; no designer API change and no Logfire config.
- `uv run --with` leaves `pyproject.toml` and `uv.lock` untouched.

## Caveats

- Traces contain the full PRD and generated test cases. Local only; do not commit or share.
- Each run costs one designer call.
- This is observability, not eval: coverage, labels, and judge calibration are still ticket 01/02.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| No trace in UI | endpoint must be `http://127.0.0.1:6006/v1/traces` |
| Spans have no LLM attributes | use instrumentation version 5, keep `OpenInferenceSpanProcessor()` before the exporter |
| `ModuleNotFoundError: web_test` | run with `PYTHONPATH=.` |
| Port already in use | `lsof -nP -iTCP:6006 -sTCP:LISTEN` |
