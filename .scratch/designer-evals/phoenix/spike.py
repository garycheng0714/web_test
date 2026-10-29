"""Send one designer run to a local Phoenix instance.

Run Phoenix separately:
    uvx arize-phoenix serve

Then:
    OPENCODE_API_KEY=... uv run --with openinference-instrumentation-pydantic-ai \
        python .scratch/designer-evals/phoenix/spike.py
"""

import argparse
import os

from openinference.instrumentation.pydantic_ai import OpenInferenceSpanProcessor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from pydantic_ai import Agent
from pydantic_ai.models.instrumented import InstrumentationSettings

from web_test.model import DEFAULT_DESIGN_MODEL
from web_test.paths import REPO_ROOT
from web_test.planning.designer import design_test_cases

PROJECT_NAME = "web-test-designer"


def _endpoint() -> str:
    base = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:6006")
    return base if base.rstrip("/").endswith("/v1/traces") else f"{base.rstrip('/')}/v1/traces"


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

    design = design_test_cases(prd.read_text(encoding="utf-8"))
    provider.force_flush()

    print(f"prd: {prd.relative_to(REPO_ROOT)}")
    print(f"model: {os.environ.get('WEB_TEST_DESIGN_MODEL', DEFAULT_DESIGN_MODEL)}")
    print(f"cases: {len(design.cases)}")
    print(f"open questions: {len(design.open_questions)}")
    print(f"phoenix: http://127.0.0.1:6006 -> project {PROJECT_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
