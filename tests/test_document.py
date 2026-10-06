import pytest

from web_test.document import ApprovedDocumentError, is_approved, render, write_report
from web_test.schema import QaReport

SAMPLE = {
    "requirement_summary": ["Users can sign up"],
    "coverage_areas": ["Registration"],
    "assumptions": [],
    "clarifications_needed": ["Is email verification required?"],
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
            "notes": "pipe | here",
        }
    ],
    "missing_unclear_requirements": [],
    "suggested_improvements": [],
}


def _report() -> QaReport:
    return QaReport.model_validate(SAMPLE)


def test_render_writes_draft_front_matter_and_table():
    text = render(_report())

    assert text.startswith("---\napproval: draft\n---\n")
    assert "## Test Cases" in text
    assert "| Test Case ID | Requirement IDs |" in text
    assert "TC-ACC-001" in text
    assert "FR-ACC-01" in text
    assert "pipe \\| here" in text


def test_render_marks_empty_sections():
    text = render(_report())

    assert "## Assumptions\n\nNone identified" in text
    assert "None identified" in text


def test_is_approved_reads_front_matter(tmp_path):
    draft = tmp_path / "draft.md"
    draft.write_text("---\napproval: draft\n---\n\n# x\n")
    approved = tmp_path / "approved.md"
    approved.write_text("---\napproval: approved\n---\n\n# x\n")

    assert is_approved(draft) is False
    assert is_approved(approved) is True


def test_write_report_refuses_to_overwrite_approved(tmp_path):
    target = tmp_path / "test-cases.md"
    target.write_text("---\napproval: approved\n---\n\n# x\n")

    with pytest.raises(ApprovedDocumentError):
        write_report(_report(), target)

    write_report(_report(), target, force=True)
    assert target.read_text().startswith("---\napproval: draft\n---\n")
