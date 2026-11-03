"""Write one designer eval run's durable artifacts."""

import json
from dataclasses import asdict, dataclass
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


def write_design(run_dir: Path, design: DesignOutput, rendered: str) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "design.json").write_text(design.model_dump_json(indent=2), encoding="utf-8")
    (run_dir / "test-case.md").write_text(rendered, encoding="utf-8")


def write_results(run_dir: Path, metadata: RunMetadata) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "units.json").write_text(
        json.dumps([asdict(unit) for unit in metadata.units], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (run_dir / "prd.md").write_text(metadata.prd_text, encoding="utf-8")
    (run_dir / "run.json").write_text(
        json.dumps(
            {
                "run_id": metadata.run_id,
                "prd": metadata.prd.name,
                "prd_path": str(metadata.prd.relative_to(REPO_ROOT)),
                "model": metadata.model,
                "project": metadata.project,
                "created_at": metadata.created_at.isoformat(),
                "requirements": len(metadata.requirements),
                "cases": len(metadata.design.cases),
                "claims": sum(unit.kind == UnitKind.CLAIM for unit in metadata.units),
                "units": len(metadata.units),
                "annotations": metadata.annotations,
                "usage": metadata.usage,
                **metadata.findings.model_dump(),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
