"""Run one designer eval and build Phoenix eval units.

This is ticket 01: parse the PRD, run the designer, attach one requirement span per PRD
requirement and one claim span per (case, valid requirement) pair under it, and save the run
artifacts.

Phoenix must be running:

    uvx arize-phoenix serve

Then:

    PYTHONPATH=. uv run --group eval \
        python evals/designer/run_eval.py
"""

import argparse
import os
import sys
import time
from collections.abc import Sequence
from datetime import UTC, datetime

from evals.designer.designer_eval.annotations import code_annotations
from evals.designer.designer_eval.artifacts import RunMetadata, write_design, write_results
from evals.designer.designer_eval.phoenix import (
    create_client,
    create_provider,
    create_units,
    fetch_usage,
    find_agent_span,
    instrument_designer,
    log_code_annotations,
)
from evals.designer.designer_eval.requirements import parse_requirements
from evals.designer.designer_eval.units import UnitKind, plan_units
from web_test.model import DEFAULT_DESIGN_MODEL
from web_test.paths import REPO_ROOT
from web_test.planning.cases_writer import render_document, title_from_stem
from web_test.planning.designer import design_test_cases

RUNS_DIR = REPO_ROOT / "evals" / "designer" / "runs"
DEFAULT_PROJECT = "web-test-designer-eval"


def log_annotations(client, annotations, *, attempts: int = 3) -> None:
    """Write CODE annotations, retrying while the spans created moments ago are still indexed."""
    for attempt in range(1, attempts + 1):
        try:
            log_code_annotations(client, annotations)
            return
        except Exception:
            if attempt == attempts:
                raise
            time.sleep(2)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
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
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    prd = (REPO_ROOT / args.prd).resolve()
    prd_text = prd.read_text(encoding="utf-8")
    model = os.environ.get("WEB_TEST_DESIGN_MODEL", DEFAULT_DESIGN_MODEL)
    run_id = args.run_id or f"{prd.stem}-{datetime.now(UTC):%Y%m%dT%H%M%SZ}"
    run_dir = RUNS_DIR / run_id

    provider = create_provider(args.project, run_id, prd.name)
    instrument_designer(provider, args.instrumentation_version)

    print(f"running designer for {prd.name}...", file=sys.stderr)
    run_start = datetime.now(UTC)
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
    plan = plan_units(
        prd_name=prd.name,
        design=design,
        requirements=requirements,
        run_id=run_id,
    )
    print(f"creating {len(plan.units)} eval units...", file=sys.stderr)
    units = create_units(provider, agent_span, plan.units)
    print("eval units created", file=sys.stderr)

    usage = fetch_usage(client, args.project, trace_id)
    annotations = code_annotations(units, design)
    write_results(
        run_dir,
        RunMetadata(
            run_id=run_id,
            prd=prd,
            prd_text=prd_text,
            model=model,
            project=args.project,
            created_at=datetime.now(UTC),
            design=design,
            requirements=requirements,
            units=units,
            findings=plan.findings,
            usage=usage,
            annotations=len(annotations),
        ),
    )

    try:
        log_annotations(client, annotations)
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
    print(f"claims: {sum(unit.kind == UnitKind.CLAIM for unit in units)}")
    print(f"annotations: {len(annotations)}")
    print(f"usage: {usage}")
    print(f"artifacts: {run_dir.relative_to(REPO_ROOT)}")
    print(f"phoenix: http://127.0.0.1:6006 -> project {args.project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
