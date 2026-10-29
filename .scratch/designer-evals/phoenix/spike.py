"""Send one designer run to a local Phoenix instance.

Run Phoenix separately:
    uvx arize-phoenix serve

Then:
    OPENCODE_API_KEY=... uv run --with openinference-instrumentation-pydantic-ai \
        --with arize-phoenix-client \
        python .scratch/designer-evals/phoenix/spike.py
"""

import argparse
import os
import sys
import time
from datetime import datetime, timedelta, timezone

from openinference.instrumentation.pydantic_ai import OpenInferenceSpanProcessor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from phoenix.client import Client
from phoenix.client.resources.spans import SpanAnnotationData
from pydantic_ai import Agent
from pydantic_ai.models.instrumented import InstrumentationSettings

from web_test.model import DEFAULT_DESIGN_MODEL
from web_test.paths import REPO_ROOT
from web_test.planning.designer import design_test_cases

PROJECT_NAME = "web-test-designer"


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


def _agent_span(client: Client, run_start: datetime) -> dict | None:
    for _ in range(10):
        spans = client.spans.get_spans(
            project_identifier=PROJECT_NAME,
            start_time=run_start - timedelta(seconds=5),
            span_kind="AGENT",
            limit=10,
        )
        if spans:
            return max(spans, key=lambda span: span["start_time"])
        time.sleep(0.5)
    return None


def _annotation(design, prd, span_id: str) -> SpanAnnotationData:
    case_count = len(design.cases)
    return SpanAnnotationData(
        name="case_count",
        annotator_kind="CODE",
        span_id=span_id,
        result={
            "score": float(case_count),
            "explanation": f"{case_count} cases",
        },
        metadata={
            "prd": prd.name,
            "case_count": case_count,
            "open_questions": len(design.open_questions),
        },
    )


def _verify_annotation(client: Client, span_id: str) -> list:
    for _ in range(10):
        annotations = client.spans.get_span_annotations(
            span_ids=[span_id],
            project_identifier=PROJECT_NAME,
            include_annotation_names=["case_count"],
        )
        if annotations:
            return annotations
        time.sleep(0.2)
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Trace one designer run into Phoenix.")
    parser.add_argument("--prd", default="prd/register-login.md")
    parser.add_argument(
        "--instrumentation-version",
        type=int,
        choices=(2, 5),
        default=5,
        help="Pydantic AI instrumentation format (default: 5)",
    )
    args = parser.parse_args()

    prd = (REPO_ROOT / args.prd).resolve()
    provider = _provider()
    Agent.instrument_all(
        InstrumentationSettings(
            version=args.instrumentation_version,
            tracer_provider=provider,
        )
    )

    run_start = datetime.now(timezone.utc)
    design = design_test_cases(prd.read_text(encoding="utf-8"))
    provider.force_flush()

    client = Client(base_url=_base_url())
    span = _agent_span(client, run_start)
    if span is None:
        print("annotation failed: designer agent span not found", file=sys.stderr)
        return 1

    span_id = span["context"]["span_id"]
    annotation = _annotation(design, prd, span_id)
    inserted = client.spans.log_span_annotations(
        span_annotations=[annotation],
        sync=True,
    )
    verified = _verify_annotation(client, span_id)
    if not verified:
        print("annotation failed: case_count not found after logging", file=sys.stderr)
        return 1

    print(f"prd: {prd.relative_to(REPO_ROOT)}")
    print(f"model: {os.environ.get('WEB_TEST_DESIGN_MODEL', DEFAULT_DESIGN_MODEL)}")
    print(f"cases: {len(design.cases)}")
    print(f"open questions: {len(design.open_questions)}")
    print(f"annotation: case_count={len(design.cases)} span={span_id}")
    print(f"annotation id: {inserted[0]['id'] if inserted else 'n/a'}")
    print(f"phoenix: http://127.0.0.1:6006 -> project {PROJECT_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
