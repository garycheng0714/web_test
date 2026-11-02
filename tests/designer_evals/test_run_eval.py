import pytest

from evals.designer.designer_eval.requirements import Requirement, parse_requirements
from evals.designer.designer_eval.units import (
    UnitKind,
    case_id,
    duplicate_groups,
    normalize_requirement_id,
    plan_units,
)
from web_test.planning.schema import Case, CaseType, DesignOutput


def _case(
    requirement_ids: list[str],
    scenario: str = "Register",
    test_type: str = "Functional",
) -> Case:
    return Case.model_validate(
        {
            "requirement_ids": requirement_ids,
            "module_feature": "Account",
            "test_scenario": scenario,
            "preconditions": ["Guest is on /login"],
            "steps": [{"action": "Signup", "expected_result": "Account page shown"}],
            "priority": "High",
            "severity": "Major",
            "test_type": test_type,
        }
    )


def _requirements() -> list[Requirement]:
    return [
        Requirement(id="FR-1", title="One", text="### FR-1 One\n- detail"),
        Requirement(id="FR-2", title="Two", text="### FR-2 Two\n- detail"),
    ]


def test_parse_requirements_stops_at_the_next_section():
    prd = """# PRD

### FR-ACC-01 First requirement
- first detail

### FR-ACC-02 Second requirement
- second detail

## 5. Next section
- not a requirement
"""

    requirements = parse_requirements(prd)

    assert [requirement.id for requirement in requirements] == ["FR-ACC-01", "FR-ACC-02"]
    assert requirements[0].title == "First requirement"
    assert "### FR-ACC-01 First requirement" in requirements[0].text
    assert "Next section" not in requirements[1].text


def test_parse_requirements_accepts_four_hash_fr_headings():
    prd = """# PRD

### 4.1 Account

#### FR-ACC-01 First requirement
- first detail

#### FR-ACC-02 Second requirement
- second detail

## 5. Next section
"""

    requirements = parse_requirements(prd)

    assert [requirement.id for requirement in requirements] == ["FR-ACC-01", "FR-ACC-02"]
    assert "#### FR-ACC-01 First requirement" in requirements[0].text


def test_parse_requirements_requires_an_fr_heading():
    with pytest.raises(ValueError, match="no FR-\\* requirements"):
        parse_requirements("# PRD\n\n## 1. Scope\n- nothing")


def test_case_id_uses_index_and_test_type():
    assert case_id(1, CaseType.UI) == "case-1-ui"
    assert case_id(6, CaseType.DATA_PERSISTENCE) == "case-6-data-persistence"


def test_normalize_requirement_id_maps_ac_ids_to_parent():
    assert normalize_requirement_id("FR-ACC-04-AC1") == "FR-ACC-04"
    assert normalize_requirement_id("FR-ACC-04") == "FR-ACC-04"
    assert normalize_requirement_id("MSG-LOGIN-TITLE") == "MSG-LOGIN-TITLE"


def test_plan_units_builds_requirement_and_claim_units():
    requirements = [
        Requirement(id="FR-ACC-01", title="One", text="### FR-ACC-01 One"),
        Requirement(id="FR-ACC-02", title="Two", text="### FR-ACC-02 Two"),
    ]
    design = DesignOutput(
        cases=[
            _case(["FR-ACC-01", "MSG-X", "FR-ACC-01-AC1"]),
            _case(["FR-ACC-02", "FR-99"], "Login", "Negative"),
        ]
    )

    plan = plan_units(
        prd_name="prd.md",
        design=design,
        requirements=requirements,
        run_id="run-1",
    )

    requirement_units = [unit for unit in plan.units if unit.kind == UnitKind.REQUIREMENT]
    claims = [unit for unit in plan.units if unit.kind == UnitKind.CLAIM]
    assert [unit.target_id for unit in requirement_units] == ["FR-ACC-01", "FR-ACC-02"]
    assert [unit.target_id for unit in claims] == [
        "case-1-functional->FR-ACC-01",
        "case-2-negative->FR-ACC-02",
    ]
    assert claims[0].parent_target_id == "FR-ACC-01"
    assert claims[0].attributes["claim.requirement_raw_ids"] == ('["FR-ACC-01", "FR-ACC-01-AC1"]')
    assert claims[0].attributes["output.mime_type"] == "text/markdown"
    assert claims[0].attributes["output.value"].startswith("## Case 1:")
    assert plan.findings.non_requirement_ids == {"case-1-functional": ["MSG-X"]}
    assert plan.findings.invalid_requirement_ids == {"case-2-negative": ["FR-99"]}
    assert plan.findings.multi_requirement_cases == []


def test_plan_units_marks_a_missing_requirement():
    design = DesignOutput(cases=[_case(["FR-1"])])

    plan = plan_units(
        prd_name="prd.md",
        design=design,
        requirements=_requirements(),
        run_id="run-1",
    )

    missing = next(unit for unit in plan.units if unit.target_id == "FR-2")
    assert missing.kind == UnitKind.REQUIREMENT
    assert missing.name == "requirement FR-2 (missing)"
    assert missing.attributes["requirement.missing"] == "true"
    assert missing.attributes["requirement.claim_count"] == "0"


def test_plan_units_deduplicates_requirement_ids():
    design = DesignOutput(cases=[_case(["FR-1", "FR-1"])])

    plan = plan_units(
        prd_name="prd.md",
        design=design,
        requirements=_requirements(),
        run_id="run-1",
    )

    claims = [unit for unit in plan.units if unit.kind == UnitKind.CLAIM]
    assert [unit.target_id for unit in claims] == ["case-1-functional->FR-1"]


def test_plan_units_flags_multi_requirement_cases():
    design = DesignOutput(cases=[_case(["FR-1", "FR-2"])])

    plan = plan_units(
        prd_name="prd.md",
        design=design,
        requirements=_requirements(),
        run_id="run-1",
    )

    claims = [unit for unit in plan.units if unit.kind == UnitKind.CLAIM]
    assert [unit.target_id for unit in claims] == [
        "case-1-functional->FR-1",
        "case-1-functional->FR-2",
    ]
    assert claims[0].attributes["claim.multi_requirement_case"] == "true"
    assert plan.findings.multi_requirement_cases == ["case-1-functional"]


def test_duplicate_groups_detects_identical_cases():
    design = DesignOutput(
        cases=[
            _case(["FR-1"]),
            _case(["FR-2"]),
            _case(["FR-3"], "Login"),
        ]
    )

    groups = duplicate_groups(design)

    assert list(groups.values()) == [["case-1-functional", "case-2-functional"]]
