"""Read and write one designer eval run's durable artifacts."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from evals.designer.designer_eval.requirements import Requirement
from evals.designer.designer_eval.units import EvalUnit, RunFindings, UnitKind
from web_test.paths import REPO_ROOT
from web_test.planning.schema import DesignOutput


@dataclass(frozen=True)
class RunMetadata:
    run_id: str
    prd: Path
    prd_text: str
    model: str
    project: str
    created_at: datetime
    design: DesignOutput
    requirements: list[Requirement]
    units: list[EvalUnit]
    findings: RunFindings
    usage: dict[str, int]
    annotations: int


class RunSummary(RunFindings):
    """`run.json`: the run metadata with the findings flattened in, so one file answers both.

    Every field is required: a run is only worth reading back when it recorded all of them, and
    the runs from before these fields existed are not read any more. Inheriting `RunFindings` keeps
    the fields declared once and makes a name collision a `TypeError` at write time instead of one
    value silently overwriting the other.
    """

    run_id: str
    prd: str
    prd_path: str
    model: str
    project: str
    created_at: datetime
    requirements: int
    cases: int
    claims: int
    units: int
    annotations: int
    usage: dict[str, int]


def write_design(run_dir: Path, design: DesignOutput, rendered: str) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "design.json").write_text(design.model_dump_json(indent=2), encoding="utf-8")
    (run_dir / "test-case.md").write_text(rendered, encoding="utf-8")


def write_results(run_dir: Path, metadata: RunMetadata) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "units.json").write_text(
        json.dumps([unit.model_dump() for unit in metadata.units], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (run_dir / "prd.md").write_text(metadata.prd_text, encoding="utf-8")
    summary = RunSummary(
        run_id=metadata.run_id,
        prd=metadata.prd.name,
        prd_path=str(metadata.prd.relative_to(REPO_ROOT)),
        model=metadata.model,
        project=metadata.project,
        created_at=metadata.created_at,
        requirements=len(metadata.requirements),
        cases=len(metadata.design.cases),
        claims=sum(unit.kind == UnitKind.CLAIM for unit in metadata.units),
        units=len(metadata.units),
        annotations=metadata.annotations,
        usage=metadata.usage,
        **metadata.findings.model_dump(),
    )
    (run_dir / "run.json").write_text(summary.model_dump_json(indent=2), encoding="utf-8")


def read_run(run_dir: Path) -> RunSummary:
    return RunSummary.model_validate_json((run_dir / "run.json").read_text(encoding="utf-8"))


def read_units(run_dir: Path) -> list[EvalUnit]:
    rows = json.loads((run_dir / "units.json").read_text(encoding="utf-8"))
    return [EvalUnit.model_validate(row) for row in rows]


def read_design(run_dir: Path) -> DesignOutput:
    return DesignOutput.model_validate_json((run_dir / "design.json").read_text(encoding="utf-8"))
