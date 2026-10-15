import pytest
from pydantic import ValidationError
from pydantic_ai.models.test import TestModel

from web_test.planning.designer import design_test_cases
from web_test.planning.schema import Case, CaseType, DesignOutput


def _case(**overrides):
    return {
        "requirement_ids": ["FR-ACC-01"],
        "module_feature": "Account",
        "test_scenario": "Verify that a new user can sign up",
        "preconditions": ["The signup page is open"],
        "steps": [
            {"action": "Enter a name", "expected_result": "The name is accepted"},
            {"action": "Click Signup", "expected_result": "The account information page is shown"},
        ],
        "priority": "High",
        "severity": "Critical",
        "test_type": "Functional",
        "notes": "",
        **overrides,
    }


def test_design_test_cases_returns_cases_and_open_questions():
    args = {"cases": [_case()], "open_questions": ["What is the password policy?"]}
    model = TestModel(custom_output_args=args, call_tools=[])

    result = design_test_cases("# PRD\n\nUsers can sign up.", model=model)

    assert isinstance(result, DesignOutput)
    case = result.cases[0]
    assert isinstance(case, Case)
    assert case.requirement_ids == ["FR-ACC-01"]
    assert case.test_type is CaseType.FUNCTIONAL
    assert case.steps[0].action == "Enter a name"
    assert case.steps[0].expected_result == "The name is accepted"
    assert result.open_questions == ["What is the password policy?"]


def test_case_rejects_an_unknown_test_type():
    with pytest.raises(ValidationError):
        Case.model_validate(_case(test_type="Nope"))
