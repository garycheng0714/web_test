import pytest
from pydantic import ValidationError
from pydantic_ai.models.test import TestModel

from web_test.planning.designer import design_test_cases
from web_test.planning.schema import CaseStatus, CaseType, QaReport

SAMPLE = {
    "requirement_summary": ["Users can sign up for an account"],
    "coverage_areas": ["Registration"],
    "assumptions": ["Email addresses are unique"],
    "clarifications_needed": [],
    "test_cases": [
        {
            "test_case_id": "TC-ACC-001",
            "requirement_ids": ["FR-ACC-01"],
            "module_feature": "Account",
            "test_scenario": "Verify that a new user can sign up",
            "preconditions": ["The signup page is open"],
            "test_steps": ["Enter a name", "Enter an unused email", "Click Signup"],
            "test_data": "name=Alice; email=alice@example.com",
            "expected_result": "The account information page is shown",
            "priority": "High",
            "severity": "Critical",
            "test_type": "Functional",
            "status": "NotRun",
            "notes": "",
        }
    ],
    "missing_unclear_requirements": [],
    "suggested_improvements": [],
}


def test_design_test_cases_returns_a_qa_report():
    model = TestModel(custom_output_args=SAMPLE, call_tools=[])

    report = design_test_cases("# PRD\n\nUsers can sign up.", model=model)

    assert isinstance(report, QaReport)
    case = report.test_cases[0]
    assert case.requirement_ids == ["FR-ACC-01"]
    assert case.test_type is CaseType.FUNCTIONAL
    assert case.status is CaseStatus.NOT_RUN


def test_qa_report_rejects_an_unknown_test_type():
    bad = {
        **SAMPLE,
        "test_cases": [{**SAMPLE["test_cases"][0], "test_type": "Nope"}],
    }

    with pytest.raises(ValidationError):
        QaReport.model_validate(bad)
