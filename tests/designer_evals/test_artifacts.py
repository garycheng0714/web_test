import json
from datetime import UTC, datetime

from evals.designer.designer_eval.artifacts import RunMetadata, write_design, write_results
from evals.designer.designer_eval.requirements import Requirement
from evals.designer.designer_eval.units import EvalUnit, RunFindings, UnitKind
from web_test.paths import REPO_ROOT
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


def _metadata() -> RunMetadata:
    return RunMetadata(
        run_id="run-1",
        prd=REPO_ROOT / "prd" / "register-login.md",
        prd_text="# PRD\n",
        model="openai-chat:deepseek-v4.1-flash",
        project="web-test-designer-eval",
        created_at=datetime(2026, 10, 29, 7, 9, 4, tzinfo=UTC),
        design=_design(),
        requirements=[Requirement(id="FR-1", title="One", text="### FR-1 One")],
        units=[
            EvalUnit(
                kind=UnitKind.CLAIM,
                target_id="case-1-functional->FR-1",
                span_id="span-1",
                name="claim case-1-functional -> FR-1",
                attributes={"claim.requirement_id": "FR-1"},
            )
        ],
        findings=RunFindings(multi_requirement_cases=["case-1-functional"]),
        usage={"prompt": 10, "completion": 2, "total": 12, "cache_read": 0},
        annotations=1,
    )


def test_write_design_writes_design_and_rendered_markdown(tmp_path):
    design = _design()

    write_design(tmp_path / "run", design, "# rendered\n")

    written = (tmp_path / "run" / "design.json").read_text()
    assert DesignOutput.model_validate_json(written) == design
    assert (tmp_path / "run" / "test-case.md").read_text() == "# rendered\n"


def test_write_results_writes_units_run_metadata_and_prd(tmp_path):
    run_dir = tmp_path / "run"
    metadata = _metadata()

    write_results(run_dir, metadata)

    units = json.loads((run_dir / "units.json").read_text())
    run = json.loads((run_dir / "run.json").read_text())

    assert units == [
        {
            "kind": "claim",
            "target_id": "case-1-functional->FR-1",
            "span_id": "span-1",
            "name": "claim case-1-functional -> FR-1",
            "attributes": {"claim.requirement_id": "FR-1"},
            "parent_span_id": None,
        }
    ]
    assert (run_dir / "prd.md").read_text() == "# PRD\n"
    assert run == {
        "run_id": "run-1",
        "prd": "register-login.md",
        "prd_path": "prd/register-login.md",
        "model": "openai-chat:deepseek-v4.1-flash",
        "project": "web-test-designer-eval",
        "created_at": "2026-10-29T07:09:04+00:00",
        "requirements": 1,
        "cases": 1,
        "claims": 1,
        "units": 1,
        "annotations": 1,
        "usage": {"prompt": 10, "completion": 2, "total": 12, "cache_read": 0},
        "non_requirement_ids": {},
        "invalid_requirement_ids": {},
        "multi_requirement_cases": ["case-1-functional"],
    }
