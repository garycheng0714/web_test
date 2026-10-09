import pytest
from pydantic_ai.models.test import TestModel

from web_test.planning.document import ApprovedDocumentError
from web_test.planning.plan import generate_test_cases
from web_test.planning.schema import QaReport

SAMPLE = {
    "requirement_summary": ["Users can sign up"],
    "coverage_areas": ["Registration"],
    "assumptions": [],
    "clarifications_needed": [],
    "test_cases": [
        {
            "test_case_id": "TC-ACC-001",
            "requirement_ids": ["FR-ACC-01"],
            "module_feature": "Account",
            "test_scenario": "Verify that a new user can sign up",
            "preconditions": ["The signup page is open"],
            "test_steps": ["Enter a name", "Click Signup"],
            "test_data": "name=Alice",
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


def _model() -> TestModel:
    return TestModel(custom_output_args=SAMPLE, call_tools=[])


def test_generate_test_cases_writes_a_draft_document(tmp_path):
    prd = tmp_path / "prd.md"
    prd.write_text("# PRD\n\nUsers can sign up.\n")
    output = tmp_path / "test-cases.md"

    report = generate_test_cases(prd, output, model=_model())

    assert isinstance(report, QaReport)
    text = output.read_text(encoding="utf-8")
    assert text.startswith("---\napproval: draft\n---\n")
    assert "| Test Case ID |" in text
    assert "TC-ACC-001" in text


def test_generate_test_cases_refuses_to_overwrite_approved(tmp_path):
    prd = tmp_path / "prd.md"
    prd.write_text("# PRD\n")
    output = tmp_path / "test-cases.md"
    output.write_text("---\napproval: approved\n---\n")

    with pytest.raises(ApprovedDocumentError):
        generate_test_cases(prd, output, model=_model())

    generate_test_cases(prd, output, model=_model(), force=True)
    assert output.read_text(encoding="utf-8").startswith("---\napproval: draft\n---\n")
