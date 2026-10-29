# Designer + Phoenix spike

Throwaway spike: send one designer run to a local Phoenix instance. This does not touch
`web_test/planning/designer.py` or the eval tickets (01–04).

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
  --with arize-phoenix-client \
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

## Annotation

After each run, `spike.py` writes a `CODE` annotation `case_count` to the designer agent span:

- `result.score` = number of generated cases
- `result.explanation` = `"N cases"`
- `metadata` = PRD name, case count, open-question count

This is a probe for the annotation pipeline, not the ticket 02 coverage evaluator.

Verify in the Phoenix UI (agent span -> annotations) or:

```bash
uv run --with arize-phoenix-client python - <<'PY'
from phoenix.client import Client

client = Client(base_url="http://127.0.0.1:6006")
print(client.spans.get_span_annotations(
    span_ids=["<span_id>"],
    project_identifier="web-test-designer",
    include_annotation_names=["case_count"],
))
PY
```

`spike_register.py` is the comparison script and does not annotate.

## Late child span probe

`late_child_probe.py` adds a new `EVALUATOR` span under an existing designer agent span *after*
that span has ended. This checks whether Phase 1 can attach requirement/case eval spans to the
original trace instead of starting a new one.

```bash
uv run --with arize-phoenix-client \
  --with openinference-instrumentation-pydantic-ai \
  python .scratch/designer-evals/phoenix/late_child_probe.py
```

Result on 2026-10-29:

```text
child span: late-child-check (EVALUATOR)
trace: 4ae60dda7197906d0e8d069a9797f8ef same=True
parent: 0d78c9b5ac90496a correct=True
```

So the late-child approach works: Phase 1 can create requirement/case `EVALUATOR` spans after
the designer run and keep them in the same Phoenix trace.

## Manual vs `register()`

`spike.py` is the baseline: manual `TracerProvider` + `OpenInferenceSpanProcessor` + exporter.
`spike_register.py` uses `phoenix.otel.register()` but still adds the Pydantic AI translator:

```bash
PYTHONPATH=. uv run --with openinference-instrumentation-pydantic-ai \
  --with arize-phoenix-otel \
  python .scratch/designer-evals/phoenix/spike_register.py
```

It writes to project `web-test-designer-register`.

`register()` alone is not enough for Pydantic AI: `arize-phoenix-otel` depends on the generic
`openinference-instrumentation`, not `openinference-instrumentation-pydantic-ai`, and the
latter has no `openinference_instrumentor` entry point. The script therefore replaces
`register()`'s default processor with `OpenInferenceSpanProcessor`, then adds the OTLP
exporter after it; otherwise export runs before translation.

## Findings (2026-10-29)

- `openinference-instrumentation-pydantic-ai==0.1.30` works with `pydantic-ai==2.54.0` on
  Python 3.13.
- `InstrumentationSettings(version=5)` maps cleanly; span names are `invoke_agent` /
  `execute_tool`.
- `version=2` also mapped, but Pydantic AI deprecates versions 2–4. Use 5.
- `Agent.instrument_all(...)` is enough; no designer API change and no Logfire config.
- `uv run --with` leaves `pyproject.toml` and `uv.lock` untouched.
- `arize-phoenix-otel==0.17.2` plus `openinference-instrumentation-pydantic-ai==0.1.30`
  with the translator before the exporter produced the same four spans and attributes as
  the manual setup.
- `register()` only (no translator) is expected to lack `llm.*` / `input.value`; that is why
  `spike_register.py` rebuilds the processor chain instead of using the default.
- `arize-phoenix-client==3.5.0` can log and read the `case_count` annotation. Its `get_spans`
  does not accept `sort` / `order`, so `spike.py` picks the newest span locally.
- A child span created after the parent ended still lands in the same trace with the correct
  parent (see `late_child_probe.py`), so Phase 1 does not need a separate eval trace.

## Caveats

- Traces contain the full PRD and generated test cases. Local only; do not commit or share.
- Each run costs one designer call.
- This is observability, not eval: units, coverage, labels, and judge calibration are still
  tickets 01–03.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| No trace in UI | endpoint must be `http://127.0.0.1:6006/v1/traces` |
| Spans have no LLM attributes | use instrumentation version 5, keep `OpenInferenceSpanProcessor()` before the exporter; `register()` alone does not add the Pydantic AI translator |
| `ModuleNotFoundError: web_test` | run with `PYTHONPATH=.` |
| Port already in use | `lsof -nP -iTCP:6006 -sTCP:LISTEN` |
