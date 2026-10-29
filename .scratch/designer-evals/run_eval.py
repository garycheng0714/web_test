"""Run one designer eval and build Phoenix eval units.

This is ticket 01: parse the PRD, run the designer, attach one EVALUATOR span per
requirement and per case under the designer agent trace, and save the run artifacts.

Phoenix must be running:

    uvx arize-phoenix serve

Then:

    PYTHONPATH=. uv run --with openinference-instrumentation-pydantic-ai \
        --with arize-phoenix-client \
        python .scratch/designer-evals/run_eval.py

Code annotations and the coverage report belong to ticket 02.
"""

import argparse
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from web_test.model import DEFAULT_DESIGN_MODEL
from web_test.paths import REPO_ROOT
from web_test.planning.cases_writer import render_document, title_from_stem
from web_test.planning.designer import design_test_cases
from web_test.planning.schema import DesignOutput

RUNS_DIR = REPO_ROOT / ".scratch" / "designer-evals" / "runs"
DEFAULT_PROJECT = "web-test-designer-eval"
_REQUIREMENT = re.compile(r"^###\s+(FR-[A-Z]+-\d+)\s*(.*)$")
_HEADING = re.compile(r"^#{2,3}\s")


@dataclass(frozen=True)
class Requirement:
    id: str
    title: str
    text: str


@dataclass(frozen=True)
class UnitSpec:
    kind: str
    target_id: str
    name: str
    attributes: dict[str, str]


@dataclass(frozen=True)
class EvalUnit:
    kind: str
    target_id: str
    span_id: str
    name: str
    attributes: dict[str, str]


def parse_requirements(prd_text: str) -> list[Requirement]:
    """Extract `### FR-*` sections, stopping at the next `##` or `###` heading."""
    requirements: list[Requirement] = []
    current_id: str | None = None
    current_title = ""
    lines: list[str] = []

    def flush() -> None:
        nonlocal current_id, current_title, lines
        if current_id is not None:
            requirements.append(
                Requirement(
                    id=current_id,
                    title=current_title,
                    text="\n".join(lines).strip(),
                )
            )
        current_id = None
        current_title = ""
        lines = []

    for line in prd_text.splitlines():
        match = _REQUIREMENT.match(line)
        if match:
            flush()
            current_id = match.group(1)
            current_title = match.group(2).strip()
            lines = [line]
            continue
        if current_id is not None and _HEADING.match(line):
            flush()
            continue
        if current_id is not None:
            lines.append(line)

    flush()
    if not requirements:
        raise ValueError("no FR-* requirements found in PRD")
    return requirements


def case_id(index: int) -> str:
    return f"case-{index}"


def _case_name(index: int, scenario: str) -> str:
    short = " ".join(scenario.split())
    if len(short) > 60:
        short = f"{short[:57]}..."
    return f"case {index}: {short}"


def plan_units(
    *,
    prd_name: str,
    design: DesignOutput,
    requirements: list[Requirement],
    run_id: str,
) -> list[UnitSpec]:
    by_id = {requirement.id: requirement for requirement in requirements}
    units: list[UnitSpec] = []

    for requirement in requirements:
        claimed = [
            (index, case)
            for index, case in enumerate(design.cases, start=1)
            if requirement.id in case.requirement_ids
        ]
        units.append(
            UnitSpec(
                kind="requirement",
                target_id=requirement.id,
                name=f"requirement {requirement.id}",
                attributes={
                    "openinference.span.kind": "EVALUATOR",
                    "requirement.id": requirement.id,
                    "input.value": requirement.text,
                    "output.value": json.dumps(
                        [
                            {
                                "case_id": case_id(index),
                                "test_scenario": case.test_scenario,
                            }
                            for index, case in claimed
                        ],
                        ensure_ascii=False,
                    ),
                    "requirement.claimed_by": json.dumps(
                        [case_id(index) for index, _ in claimed],
                        ensure_ascii=False,
                    ),
                    "designer.run.id": run_id,
                    "designer.prd": prd_name,
                },
            )
        )

    for index, case in enumerate(design.cases, start=1):
        invented = [
            requirement_id
            for requirement_id in case.requirement_ids
            if requirement_id not in by_id
        ]
        units.append(
            UnitSpec(
                kind="case",
                target_id=case_id(index),
                name=_case_name(index, case.test_scenario),
                attributes={
                    "openinference.span.kind": "EVALUATOR",
                    "case.id": case_id(index),
                    "input.value": case.model_dump_json(),
                    "output.value": json.dumps(
                        {
                            requirement_id: by_id[requirement_id].text
                            for requirement_id in case.requirement_ids
                            if requirement_id in by_id
                        },
                        ensure_ascii=False,
                    ),
                    "case.requirement_ids": json.dumps(
                        case.requirement_ids, ensure_ascii=False
                    ),
                    "case.invented_requirement_ids": json.dumps(
                        invented, ensure_ascii=False
                    ),
                    "designer.run.id": run_id,
                    "designer.prd": prd_name,
                },
            )
        )

    return units


def _endpoint() -> str:
    base = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:6006")
    return base if base.rstrip("/").endswith("/v1/traces") else f"{base.rstrip('/')}/v1/traces"


def _base_url() -> str:
    return _endpoint().removesuffix("/v1/traces")


def _provider(project: str, run_id: str, prd_name: str):
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
    provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint=_endpoint())))
    trace.set_tracer_provider(provider)
    return provider


def _agent_span(client, project: str, run_start: datetime) -> dict | None:
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


def _create_units(provider, agent_span: dict, specs: list[UnitSpec]) -> list[EvalUnit]:
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


def _write_run(
    run_dir: Path,
    *,
    run_id: str,
    prd: Path,
    model: str,
    project: str,
    design: DesignOutput,
    requirements: list[Requirement],
    units: list[EvalUnit],
    rendered: str,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "design.json").write_text(design.model_dump_json(indent=2), encoding="utf-8")
    (run_dir / "test-case.md").write_text(rendered, encoding="utf-8")
    (run_dir / "units.json").write_text(
        json.dumps([asdict(unit) for unit in units], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (run_dir / "run.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "prd": prd.name,
                "model": model,
                "project": project,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "requirements": len(requirements),
                "cases": len(design.cases),
                "units": len(units),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Phoenix eval units for one designer run.")
    parser.add_argument("--prd", default="prd/register-login.md")
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--base-url", default="https://automationexercise.com")
    parser.add_argument("--run-id")
    parser.add_argument(
        "--instrumentation-version",
        type=int,
        choices=(2, 5),
        default=5,
        help="Pydantic AI instrumentation format (default: 5)",
    )
    args = parser.parse_args()

    from phoenix.client import Client
    from pydantic_ai import Agent
    from pydantic_ai.models.instrumented import InstrumentationSettings

    prd = (REPO_ROOT / args.prd).resolve()
    prd_text = prd.read_text(encoding="utf-8")
    model = os.environ.get("WEB_TEST_DESIGN_MODEL", DEFAULT_DESIGN_MODEL)
    run_id = args.run_id or f"{prd.stem}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    run_dir = RUNS_DIR / run_id

    provider = _provider(args.project, run_id, prd.name)
    Agent.instrument_all(
        InstrumentationSettings(
            version=args.instrumentation_version,
            tracer_provider=provider,
        )
    )

    run_start = datetime.now(timezone.utc)
    design = design_test_cases(prd_text)
    provider.force_flush()

    client = Client(base_url=_base_url())
    agent_span = _agent_span(client, args.project, run_start)
    if agent_span is None:
        print("failed: designer agent span not found", file=sys.stderr)
        return 1

    requirements = parse_requirements(prd_text)
    specs = plan_units(
        prd_name=prd.name,
        design=design,
        requirements=requirements,
        run_id=run_id,
    )
    units = _create_units(provider, agent_span, specs)
    rendered = render_document(
        design.cases,
        id=prd.stem,
        base_url=args.base_url,
        title=title_from_stem(prd.stem),
        open_questions=design.open_questions,
    )
    _write_run(
        run_dir,
        run_id=run_id,
        prd=prd,
        model=model,
        project=args.project,
        design=design,
        requirements=requirements,
        units=units,
        rendered=rendered,
    )

    print(f"run: {run_id}")
    print(f"prd: {prd.relative_to(REPO_ROOT)}")
    print(f"model: {model}")
    print(f"requirements: {len(requirements)}")
    print(f"cases: {len(design.cases)}")
    print(f"units: {len(units)}")
    print(f"artifacts: {run_dir.relative_to(REPO_ROOT)}")
    print(f"phoenix: http://127.0.0.1:6006 -> project {args.project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
