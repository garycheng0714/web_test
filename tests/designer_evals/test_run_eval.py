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


def test_plan_units_maps_requirements_to_cases_and_flags_invented_ids():
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

    assert [unit.kind for unit in units] == ["requirement", "requirement", "case", "case"]
    assert units[0].target_id == "FR-1"
    assert units[0].attributes["requirement.claimed_by"] == '["case-1"]'
    assert units[1].attributes["requirement.claimed_by"] == '["case-2"]'
    assert units[2].target_id == "case-1"
    assert units[3].target_id == "case-2"
    assert units[3].attributes["case.requirement_ids"] == '["FR-2", "FR-9"]'
    assert units[3].attributes["case.invented_requirement_ids"] == '["FR-9"]'
    assert "FR-2" in units[3].attributes["output.value"]
    assert "FR-9" not in units[3].attributes["output.value"]
    assert all(unit.attributes["designer.run.id"] == "run-1" for unit in units)
