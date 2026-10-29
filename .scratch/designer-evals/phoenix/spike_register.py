"""Compare `phoenix.otel.register()` with the manual setup in spike.py.

`register()` only wires the generic OpenInference TracerProvider; the Pydantic AI
translator is the separate `OpenInferenceSpanProcessor`. This script keeps that
processor and rebuilds the processor order so translation happens before export.

Run Phoenix separately:
    uvx arize-phoenix serve

Then:
    PYTHONPATH=. uv run --with openinference-instrumentation-pydantic-ai \
        --with arize-phoenix-otel \
        python .scratch/designer-evals/phoenix/spike_register.py
"""

import argparse
import os

from openinference.instrumentation.pydantic_ai import OpenInferenceSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from phoenix.otel import register
from pydantic_ai import Agent
from pydantic_ai.models.instrumented import InstrumentationSettings

from web_test.model import DEFAULT_DESIGN_MODEL
from web_test.paths import REPO_ROOT
from web_test.planning.designer import design_test_cases

PROJECT_NAME = "web-test-designer-register"


def _endpoint() -> str:
    base = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:6006")
    return base if base.rstrip("/").endswith("/v1/traces") else f"{base.rstrip('/')}/v1/traces"


def _provider(project: str):
    provider = register(
        project_name=project,
        endpoint=_endpoint(),
        protocol="http/protobuf",
        batch=False,
        verbose=False,
        auto_instrument=False,
    )
    # `register()` installs its exporter as the default processor and its TracerProvider
    # does not know about the Pydantic AI translator. Replace the default with the
    # translator, then append the exporter after it.
    provider.add_span_processor(
        OpenInferenceSpanProcessor(), replace_default_processor=True
    )
    provider.add_span_processor(
        SimpleSpanProcessor(OTLPSpanExporter(endpoint=_endpoint())),
        replace_default_processor=False,
    )
    return provider


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Trace one designer run into Phoenix via phoenix.otel.register()."
    )
    parser.add_argument("--prd", default="prd/register-login.md")
    parser.add_argument("--project", default=PROJECT_NAME)
    parser.add_argument(
        "--instrumentation-version",
        type=int,
        choices=(2, 5),
        default=5,
        help="Pydantic AI instrumentation format (default: 5)",
    )
    args = parser.parse_args()

    prd = (REPO_ROOT / args.prd).resolve()
    provider = _provider(args.project)
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
    print(f"phoenix: http://127.0.0.1:6006 -> project {args.project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
