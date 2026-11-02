from designer_eval.annotations import code_annotations
from designer_eval.units import EvalUnit, UnitKind

from web_test.planning.schema import Case, DesignOutput


def _case(requirement_ids: list[str], scenario: str) -> Case:
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


def _claim(
    target_id: str,
    span_id: str,
    *,
    requirement_id: str,
    case_id: str,
    exists: bool = True,
) -> EvalUnit:
    return EvalUnit(
        kind=UnitKind.CLAIM,
        target_id=target_id,
        span_id=span_id,
        name=f"claim {target_id}",
        attributes={
            "claim.requirement_id": requirement_id,
            "claim.case_id": case_id,
            "claim.requirement_exists": "true" if exists else "false",
        },
    )


def test_code_annotations_marks_valid_claims():
    design = DesignOutput(cases=[_case(["FR-1"], "Register")])
    units = [
        _claim("FR-1<-case-1", "span-1", requirement_id="FR-1", case_id="case-1"),
    ]

    annotations = code_annotations(units, design)

    assert [(item.name, item.label, item.score) for item in annotations] == [
        ("requirement_exists", "valid", 1.0),
        ("case_duplicate", "unique", 1.0),
    ]
    assert annotations[0].metadata == {
        "claim_id": "FR-1<-case-1",
        "requirement_id": "FR-1",
        "case_id": "case-1",
    }


def test_code_annotations_marks_invented_ids():
    design = DesignOutput(cases=[_case(["FR-9"], "Register")])
    units = [
        _claim(
            "FR-9<-case-1",
            "span-9",
            requirement_id="FR-9",
            case_id="case-1",
            exists=False,
        ),
    ]

    annotations = code_annotations(units, design)

    requirement_exists = next(item for item in annotations if item.name == "requirement_exists")
    assert (requirement_exists.label, requirement_exists.score) == ("invented", 0.0)


def test_code_annotations_marks_duplicate_cases():
    design = DesignOutput(
        cases=[
            _case(["FR-1"], "Register"),
            _case(["FR-2"], "Register"),
        ]
    )
    units = [
        _claim("FR-1<-case-1", "span-1", requirement_id="FR-1", case_id="case-1"),
        _claim("FR-2<-case-2", "span-2", requirement_id="FR-2", case_id="case-2"),
    ]

    annotations = code_annotations(units, design)

    duplicate = next(
        item
        for item in annotations
        if item.name == "case_duplicate" and item.metadata["case_id"] == "case-1"
    )
    assert (duplicate.label, duplicate.score) == ("duplicate", 0.0)
    assert duplicate.metadata["duplicate_with"] == ["case-2"]


def test_code_annotations_skips_missing_requirement_spans():
    design = DesignOutput(cases=[_case(["FR-1"], "Register")])
    units = [
        EvalUnit(
            kind=UnitKind.REQUIREMENT,
            target_id="FR-2",
            span_id="span-2",
            name="requirement FR-2 (missing)",
            attributes={"requirement.missing": "true"},
        )
    ]

    assert code_annotations(units, design) == []
