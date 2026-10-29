import importlib.util
from pathlib import Path

import pytest

from web_test.planning.schema import Case, DesignOutput

_MODULE_PATH = Path(__file__).parents[2] / ".scratch" / "designer-evals" / "run_eval.py"
_SPEC = importlib.util.spec_from_file_location("designer_run_eval", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
run_eval = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(run_eval)


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


def test_parse_requirements_stops_at_the_next_section():
    prd = """# PRD

### FR-ACC-01 First requirement
- first detail

### FR-ACC-02 Second requirement
- second detail

## 5. Next section
- not a requirement
"""

    requirements = run_eval.parse_requirements(prd)

    assert [requirement.id for requirement in requirements] == ["FR-ACC-01", "FR-ACC-02"]
    assert requirements[0].title == "First requirement"
    assert "### FR-ACC-01 First requirement" in requirements[0].text
    assert "first detail" in requirements[0].text
    assert "Next section" not in requirements[1].text


def test_parse_requirements_requires_an_fr_heading():
    with pytest.raises(ValueError, match="no FR-\\* requirements"):
        run_eval.parse_requirements("# PRD\n\n## 1. Scope\n- nothing")


def test_plan_units_creates_one_claim_per_pair_and_flags_invented_ids():
    requirements = [
        run_eval.Requirement(id="FR-1", title="One", text="### FR-1 One\n- detail"),
        run_eval.Requirement(id="FR-2", title="Two", text="### FR-2 Two\n- detail"),
    ]
    design = DesignOutput(
        cases=[
            _case(["FR-1"], "Register"),
            _case(["FR-2", "FR-9"], "Login"),
        ]
    )

    units = run_eval.plan_units(
        prd_name="register-login.md",
        design=design,
        requirements=requirements,
        run_id="run-1",
    )

    assert [unit.kind for unit in units] == ["claim", "claim", "claim"]
    assert [unit.target_id for unit in units] == [
        "FR-1<-case-1",
        "FR-2<-case-2",
        "FR-9<-case-2",
    ]
    assert units[0].attributes["claim.requirement_exists"] == "true"
    assert units[0].attributes["input.value"] == requirements[0].text
    assert units[2].name.endswith("(invented)")
    assert units[2].attributes["claim.requirement_exists"] == "false"
    assert units[2].attributes["input.value"] == "missing requirement id: FR-9"
    assert all(unit.attributes["designer.run.id"] == "run-1" for unit in units)


def test_plan_units_adds_a_span_for_a_missing_requirement():
    requirements = [
        run_eval.Requirement(id="FR-1", title="One", text="### FR-1 One\n- detail"),
        run_eval.Requirement(id="FR-2", title="Two", text="### FR-2 Two\n- detail"),
    ]
    design = DesignOutput(cases=[_case(["FR-1"], "Register")])

    units = run_eval.plan_units(
        prd_name="register-login.md",
        design=design,
        requirements=requirements,
        run_id="run-1",
    )

    assert [unit.kind for unit in units] == ["claim", "requirement"]
    assert units[1].target_id == "FR-2"
    assert units[1].name == "requirement FR-2 (missing)"
    assert units[1].attributes["requirement.missing"] == "true"
    assert units[1].attributes["requirement.claimed_by"] == "[]"


def test_plan_units_deduplicates_requirement_ids():
    requirements = [
        run_eval.Requirement(id="FR-1", title="One", text="### FR-1 One\n- detail"),
    ]
    design = DesignOutput(cases=[_case(["FR-1", "FR-1"], "Register")])

    units = run_eval.plan_units(
        prd_name="register-login.md",
        design=design,
        requirements=requirements,
        run_id="run-1",
    )

    assert [unit.target_id for unit in units] == ["FR-1<-case-1"]


def test_duplicate_groups_detects_identical_cases():
    design = DesignOutput(
        cases=[
            _case(["FR-1"], "Register"),
            _case(["FR-2"], "Register"),
            _case(["FR-3"], "Login"),
        ]
    )

    groups = run_eval.duplicate_groups(design)

    assert list(groups.values()) == [["case-1", "case-2"]]


def test_sum_usage_adds_llm_token_counts():
    spans = [
        {
            "attributes": {
                "llm.token_count.prompt": 10,
                "llm.token_count.completion": 2,
                "llm.token_count.total": 12,
                "llm.token_count.prompt_details.cache_read": 7,
            }
        },
        {
            "attributes": {
                "llm.token_count.prompt": 20,
                "llm.token_count.completion": 3,
                "llm.token_count.total": 23,
            }
        },
    ]

    assert run_eval._sum_usage(spans) == {
        "prompt": 30,
        "completion": 5,
        "total": 35,
        "cache_read": 7,
    }
