"""Write one designer eval run's durable artifacts."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from web_test.planning.schema import DesignOutput

from designer_eval.requirements import Requirement
from designer_eval.units import EvalUnit


@dataclass(frozen=True)
class RunMetadata:
    run_id: str
    prd: Path
    model: str
    project: str
    created_at: datetime
    design: DesignOutput
    requirements: list[Requirement]
    units: list[EvalUnit]
    usage: dict[str, int]


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
    (run_dir / "run.json").write_text(
        json.dumps(
            {
                "run_id": metadata.run_id,
                "prd": metadata.prd.name,
                "model": metadata.model,
                "project": metadata.project,
                "created_at": metadata.created_at.isoformat(),
                "requirements": len(metadata.requirements),
                "cases": len(metadata.design.cases),
                "units": len(metadata.units),
                "usage": metadata.usage,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
