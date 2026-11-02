"""Phoenix and OpenTelemetry adapter for one designer eval run."""

import os
import time
from datetime import datetime

from designer_eval.annotations import AnnotationSpec
from designer_eval.units import EvalUnit, UnitSpec

DEFAULT_ENDPOINT = "http://127.0.0.1:6006"
_USAGE_ATTRIBUTES = {
    "llm.token_count.prompt": "prompt",
    "llm.token_count.completion": "completion",
    "llm.token_count.total": "total",
    "llm.token_count.prompt_details.cache_read": "cache_read",
}


def endpoint(base: str | None = None) -> str:
    value = base or os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", DEFAULT_ENDPOINT)
    return value if value.rstrip("/").endswith("/v1/traces") else f"{value.rstrip('/')}/v1/traces"


def base_url(base: str | None = None) -> str:
    return endpoint(base).removesuffix("/v1/traces")


def create_provider(project: str, run_id: str, prd_name: str, base: str | None = None):
    from openinference.instrumentation.pydantic_ai import OpenInferenceSpanProcessor
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor

    provider = TracerProvider(
        resource=Resource.create(
            {
                "openinference.project.name": project,
                "service.name": project,
                "designer.run.id": run_id,
                "designer.prd": prd_name,
            }
        )
    )
    provider.add_span_processor(OpenInferenceSpanProcessor())
    provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint=endpoint(base))))
    trace.set_tracer_provider(provider)
    return provider


def instrument_designer(provider, version: int = 5) -> None:
    from pydantic_ai import Agent
    from pydantic_ai.models.instrumented import InstrumentationSettings

    Agent.instrument_all(InstrumentationSettings(version=version, tracer_provider=provider))


def create_client(base: str | None = None):
    from phoenix.client import Client

    return Client(base_url=base_url(base))


def find_agent_span(client, project: str, run_start: datetime) -> dict | None:
    for _ in range(10):
        spans = client.spans.get_spans(
            project_identifier=project,
            start_time=run_start,
            span_kind="AGENT",
            limit=10,
        )
        if spans:
            return max(spans, key=lambda span: span["start_time"])
        time.sleep(0.5)
    return None


def create_units(provider, agent_span: dict, specs: list[UnitSpec]) -> list[EvalUnit]:
    from opentelemetry import trace
    from opentelemetry.trace import (
        NonRecordingSpan,
        SpanContext,
        TraceFlags,
        format_span_id,
        set_span_in_context,
    )

    context = agent_span["context"]
    parent_context = set_span_in_context(
        NonRecordingSpan(
            SpanContext(
                trace_id=int(context["trace_id"], 16),
                span_id=int(context["span_id"], 16),
                is_remote=True,
                trace_flags=TraceFlags(TraceFlags.SAMPLED),
            )
        )
    )
    tracer = trace.get_tracer("designer-eval")
    units: list[EvalUnit] = []
    for spec in specs:
        with tracer.start_as_current_span(
            spec.name,
            context=parent_context,
            attributes=spec.attributes,
        ) as span:
            span_id = format_span_id(span.get_span_context().span_id)
        units.append(
            EvalUnit(
                kind=spec.kind,
                target_id=spec.target_id,
                span_id=span_id,
                name=spec.name,
                attributes=spec.attributes,
            )
        )
    provider.force_flush()
    return units


def sum_usage(spans: list[dict]) -> dict[str, int]:
    totals = {"prompt": 0, "completion": 0, "total": 0, "cache_read": 0}
    for span in spans:
        attributes = span.get("attributes", {})
        for attribute, key in _USAGE_ATTRIBUTES.items():
            value = attributes.get(attribute)
            if isinstance(value, (int, float)):
                totals[key] += int(value)
    return totals


def fetch_usage(client, project: str, trace_id: str) -> dict[str, int]:
    spans = client.spans.get_spans(
        project_identifier=project,
        trace_ids=[trace_id],
        limit=100,
    )
    return sum_usage(spans)


def log_code_annotations(client, annotations: list[AnnotationSpec]) -> None:
    from phoenix.client.resources.spans import SpanAnnotationData

    payload = [
        SpanAnnotationData(
            name=annotation.name,
            annotator_kind="CODE",
            span_id=annotation.span_id,
            result={"label": annotation.label, "score": annotation.score},
            metadata=annotation.metadata,
        )
        for annotation in annotations
    ]
    if payload:
        client.spans.log_span_annotations(span_annotations=payload, sync=True)
