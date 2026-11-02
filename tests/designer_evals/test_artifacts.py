import json
from datetime import UTC, datetime
from pathlib import Path

from designer_eval.artifacts import RunMetadata, write_design, write_results
from designer_eval.requirements import Requirement
from designer_eval.units import EvalUnit, UnitKind

from web_test.planning.schema import Case, DesignOutput


def _design() -> DesignOutput:
    return DesignOutput(
        cases=[
            Case.model_validate(
                {
                    "requirement_ids": ["FR-1"],
                    "module_feature": "Account",
                    "test_scenario": "Register",
                    "preconditions": ["Guest is on /login"],
                    "steps": [{"action": "Signup", "expected_result": "Account page shown"}],
                    "priority": "High",
                    "severity": "Major",
                    "test_type": "Functional",
                }
            )
        ]
    )


def _metadata(run_dir: Path) -> RunMetadata:
    design = _design()
    return RunMetadata(
        run_id="run-1",
        prd=Path("prd/register-login.md"),
        model="openai-chat:deepseek-v4.1-flash",
        project="web-test-designer-eval",
        created_at=datetime(2026, 10, 29, 7, 9, 4, tzinfo=UTC),
        design=design,
        requirements=[Requirement(id="FR-1", title="One", text="### FR-1 One")],
        units=[
            EvalUnit(
                kind=UnitKind.CLAIM,
                target_id="FR-1<-case-1",
                span_id="span-1",
                name="claim FR-1 <- case-1",
                attributes={"claim.requirement_id": "FR-1"},
            )
        ],
        usage={"prompt": 10, "completion": 2, "total": 12, "cache_read": 0},
    )


def test_write_design_writes_design_and_rendered_markdown(tmp_path):
    design = _design()

    write_design(tmp_path / "run", design, "# rendered\n")

    written = (tmp_path / "run" / "design.json").read_text()
    assert DesignOutput.model_validate_json(written) == design
    assert (tmp_path / "run" / "test-case.md").read_text() == "# rendered\n"


def test_write_results_writes_units_and_run_metadata(tmp_path):
    run_dir = tmp_path / "run"
    metadata = _metadata(run_dir)

    write_results(run_dir, metadata)

    units = json.loads((run_dir / "units.json").read_text())
    run = json.loads((run_dir / "run.json").read_text())

    assert units == [
        {
            "kind": "claim",
            "target_id": "FR-1<-case-1",
            "span_id": "span-1",
            "name": "claim FR-1 <- case-1",
            "attributes": {"claim.requirement_id": "FR-1"},
        }
    ]
    assert run == {
        "run_id": "run-1",
        "prd": "register-login.md",
        "model": "openai-chat:deepseek-v4.1-flash",
        "project": "web-test-designer-eval",
        "created_at": "2026-10-29T07:09:04+00:00",
        "requirements": 1,
        "cases": 1,
        "units": 1,
        "usage": {"prompt": 10, "completion": 2, "total": 12, "cache_read": 0},
    }
