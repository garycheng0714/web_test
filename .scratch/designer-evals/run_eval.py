"""Run one designer eval and build Phoenix eval units.

This is ticket 01: parse the PRD, run the designer, attach one EVALUATOR claim span per
(requirement, case) pair plus missing-requirement spans under the designer agent trace, and
save the run artifacts.

Phoenix must be running:

    uvx arize-phoenix serve

Then:

    PYTHONPATH=. uv run --group eval \
        python .scratch/designer-evals/run_eval.py
"""

import argparse
import os
import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

from web_test.model import DEFAULT_DESIGN_MODEL
from web_test.paths import REPO_ROOT
from web_test.planning.cases_writer import render_document, title_from_stem
from web_test.planning.designer import design_test_cases

from designer_eval.annotations import code_annotations
from designer_eval.artifacts import RunMetadata, write_design, write_results
from designer_eval.phoenix import (
    create_client,
    create_provider,
    create_units,
    fetch_usage,
    find_agent_span,
    instrument_designer,
    log_code_annotations,
)
from designer_eval.requirements import parse_requirements
from designer_eval.units import plan_units

RUNS_DIR = REPO_ROOT / ".scratch" / "designer-evals" / "runs"
DEFAULT_PROJECT = "web-test-designer-eval"


def main(argv: Sequence[str] | None = None) -> int:
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
    args = parser.parse_args(argv)

    prd = (REPO_ROOT / args.prd).resolve()
    prd_text = prd.read_text(encoding="utf-8")
    model = os.environ.get("WEB_TEST_DESIGN_MODEL", DEFAULT_DESIGN_MODEL)
    run_id = args.run_id or f"{prd.stem}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    run_dir = RUNS_DIR / run_id

    provider = create_provider(args.project, run_id, prd.name)
    instrument_designer(provider, args.instrumentation_version)

    print(f"running designer for {prd.name}...", file=sys.stderr)
    run_start = datetime.now(timezone.utc)
    design = design_test_cases(prd_text)
    provider.force_flush()
    print(f"designer finished: {len(design.cases)} cases", file=sys.stderr)

    rendered = render_document(
        design.cases,
        id=prd.stem,
        base_url=args.base_url,
        title=title_from_stem(prd.stem),
        open_questions=design.open_questions,
    )
    write_design(run_dir, design, rendered)
    print(f"design artifacts written: {run_dir.relative_to(REPO_ROOT)}", file=sys.stderr)

    client = create_client()
    agent_span = find_agent_span(client, args.project, run_start)
    if agent_span is None:
        print("failed: designer agent span not found", file=sys.stderr)
        return 1
    print("designer agent span found", file=sys.stderr)

    trace_id = agent_span["context"]["trace_id"]
    requirements = parse_requirements(prd_text)
    specs = plan_units(
        prd_name=prd.name,
        design=design,
        requirements=requirements,
        run_id=run_id,
    )
    print(f"creating {len(specs)} eval units...", file=sys.stderr)
    units = create_units(provider, agent_span, specs)
    print("eval units created", file=sys.stderr)

    usage = fetch_usage(client, args.project, trace_id)
    write_results(
        run_dir,
        RunMetadata(
            run_id=run_id,
            prd=prd,
            model=model,
            project=args.project,
            created_at=datetime.now(timezone.utc),
            design=design,
            requirements=requirements,
            units=units,
            usage=usage,
        ),
    )

    annotations = code_annotations(units, design)
    try:
        log_code_annotations(client, annotations)
    except Exception as error:
        print(f"failed to write code annotations: {error}", file=sys.stderr)
        return 1
    print(f"code annotations written: {len(annotations)}", file=sys.stderr)

    print(f"run: {run_id}")
    print(f"prd: {prd.relative_to(REPO_ROOT)}")
    print(f"model: {model}")
    print(f"requirements: {len(requirements)}")
    print(f"cases: {len(design.cases)}")
    print(f"units: {len(units)}")
    print(f"annotations: {len(annotations)}")
    print(f"usage: {usage}")
    print(f"artifacts: {run_dir.relative_to(REPO_ROOT)}")
    print(f"phoenix: http://127.0.0.1:6006 -> project {args.project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
