from evals.designer.designer_eval.annotations import code_annotations
from evals.designer.designer_eval.units import EvalUnit, UnitKind
from web_test.planning.schema import Case, DesignOutput


def _case(requirement_ids: list[str], scenario: str = "Register") -> Case:
    return Case.model_validate(
        {
            "requirement_ids": requirement_ids,
            "module_feature": "Account",
            "test_scenario": scenario,
            "preconditions": ["Guest is on /login"],
            "steps": [{"action": "Signup", "expected_result": "Account page shown"}],
            "priority": "High",
            "severity": "Major",
            "test_type": "Functional",
        }
    )


def _claim(target_id: str, span_id: str, *, requirement_id: str, case_id: str) -> EvalUnit:
    return EvalUnit(
        kind=UnitKind.CLAIM,
        target_id=target_id,
        span_id=span_id,
        name=f"claim {target_id}",
        attributes={
            "claim.requirement_id": requirement_id,
            "claim.case_id": case_id,
        },
    )


def test_code_annotations_marks_unique_claims():
    design = DesignOutput(cases=[_case(["FR-1"])])
    units = [
        _claim(
            "case-1-functional->FR-1",
            "span-1",
            requirement_id="FR-1",
            case_id="case-1-functional",
        ),
    ]

    annotations = code_annotations(units, design)

    assert [(item.name, item.label, item.score) for item in annotations] == [
        ("case_duplicate", "unique", 1.0)
    ]
    assert annotations[0].metadata == {
        "claim_id": "case-1-functional->FR-1",
        "case_id": "case-1-functional",
        "duplicate_with": [],
    }


def test_code_annotations_marks_duplicate_cases():
    design = DesignOutput(
        cases=[
            _case(["FR-1"]),
            _case(["FR-2"]),
        ]
    )
    units = [
        _claim(
            "case-1-functional->FR-1",
            "span-1",
            requirement_id="FR-1",
            case_id="case-1-functional",
        ),
        _claim(
            "case-2-functional->FR-2",
            "span-2",
            requirement_id="FR-2",
            case_id="case-2-functional",
        ),
    ]

    annotations = code_annotations(units, design)

    duplicate = next(
        item
        for item in annotations
        if item.name == "case_duplicate" and item.metadata["case_id"] == "case-1-functional"
    )
    assert (duplicate.label, duplicate.score) == ("duplicate", 0.0)
    assert duplicate.metadata["duplicate_with"] == ["case-2-functional"]


def test_code_annotations_skips_requirement_spans():
    design = DesignOutput(cases=[_case(["FR-1"])])
    units = [
        EvalUnit(
            kind=UnitKind.REQUIREMENT,
            target_id="FR-1",
            span_id="span-1",
            name="requirement FR-1",
            attributes={"requirement.id": "FR-1"},
        )
    ]

    assert code_annotations(units, design) == []
