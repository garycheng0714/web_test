"""Probe whether a span created after the parent ended lands in the same Phoenix trace.

Uses the existing designer trace and adds one `late-child-check` span under its agent span.
Run Phoenix separately, then:

    uv run --with arize-phoenix-client \
        --with openinference-instrumentation-pydantic-ai \
        python .scratch/designer-evals/phoenix/late_child_probe.py
"""

import os
import time

from openinference.instrumentation.pydantic_ai import OpenInferenceSpanProcessor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags, set_span_in_context
from phoenix.client import Client

PROJECT_NAME = "web-test-designer"
TRACE_ID = "4ae60dda7197906d0e8d069a9797f8ef"
AGENT_SPAN_ID = "0d78c9b5ac90496a"
CHILD_NAME = "late-child-check"


def _endpoint() -> str:
    base = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:6006")
    return base if base.rstrip("/").endswith("/v1/traces") else f"{base.rstrip('/')}/v1/traces"


def _base_url() -> str:
    return _endpoint().removesuffix("/v1/traces")


def _provider() -> TracerProvider:
    provider = TracerProvider(
        resource=Resource.create(
            {
                "openinference.project.name": PROJECT_NAME,
                "service.name": PROJECT_NAME,
            }
        )
    )
    provider.add_span_processor(OpenInferenceSpanProcessor())
    provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint=_endpoint())))
    trace.set_tracer_provider(provider)
    return provider


def _find_child(client: Client) -> dict | None:
    for _ in range(10):
        spans = client.spans.get_spans(
            project_identifier=PROJECT_NAME,
            trace_ids=[TRACE_ID],
            limit=100,
        )
        for span in spans:
            if span["name"] == CHILD_NAME:
                return span
        time.sleep(0.5)
    return None


def main() -> int:
    client = Client(base_url=_base_url())
    parent_context = set_span_in_context(
        NonRecordingSpan(
            SpanContext(
                trace_id=int(TRACE_ID, 16),
                span_id=int(AGENT_SPAN_ID, 16),
                is_remote=True,
                trace_flags=TraceFlags(TraceFlags.SAMPLED),
            )
        )
    )

    provider = _provider()
    tracer = trace.get_tracer("late-child-check")
    with tracer.start_as_current_span(
        CHILD_NAME,
        context=parent_context,
        attributes={
            "openinference.span.kind": "EVALUATOR",
            "input.value": "late child check",
            "output.value": "ok",
        },
    ):
        pass
    provider.force_flush()

    child = _find_child(client)
    if child is None:
        print("failed: child span not found in the original trace")
        return 1

    trace_id = child["context"]["trace_id"]
    parent_id = child.get("parent_id")
    same_trace = trace_id == TRACE_ID
    correct_parent = parent_id == AGENT_SPAN_ID
    print(f"child span: {child['name']} ({child['span_kind']})")
    print(f"trace: {trace_id} same={same_trace}")
    print(f"parent: {parent_id} correct={correct_parent}")
    return 0 if same_trace and correct_parent else 1


if __name__ == "__main__":
    raise SystemExit(main())
