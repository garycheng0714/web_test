from web_test.automation.case_file import CaseFile
from web_test.planning.document import render_case
from web_test.planning.schema import Case

CASE = Case.model_validate(
    {
        "requirement_ids": ["FR-CNT-01"],
        "module_feature": "Contact Us",
        "test_scenario": "Contact Us Form",
        "preconditions": ["The home page is open"],
        "steps": [
            {"action": "Click Contact Us", "expected_result": "The Contact Us page opens"},
            {
                "action": "Submit the form",
                "expected_result": "A success message is shown | with a pipe",
            },
        ],
        "priority": "High",
        "severity": "Critical",
        "test_type": "Functional",
        "notes": "Assumed the form accepts any email.",
    }
)


def test_render_case_matches_the_reference_format():
    text = render_case(CASE, id="test-case-0004", base_url="https://automationexercise.com")

    assert text.startswith(
        "---\n"
        "id: test-case-0004\n"
        "base_url: https://automationexercise.com\n"
        "requirement_ids: [FR-CNT-01]\n"
        "priority: High\n"
        "test_type: Functional\n"
        "---\n"
    )
    assert "# Contact Us: Contact Us Form" in text
    assert "**Severity:** Critical" in text
    assert "## Preconditions" in text
    assert "- The home page is open" in text
    assert "| Step | Action | Expected Result |" in text
    assert "| 1 | Click Contact Us | The Contact Us page opens |" in text
    assert "| 2 | Submit the form | A success message is shown \\| with a pipe |" in text
    assert "## Notes" in text
    assert "Assumed the form accepts any email." in text


def test_render_case_omits_empty_preconditions_and_notes():
    case = CASE.model_copy(update={"preconditions": [], "notes": ""})

    text = render_case(case, id="test-case-0005", base_url="https://example.com")

    assert "## Preconditions" not in text
    assert "## Notes" not in text


def test_rendered_front_matter_parses_with_case_file():
    text = render_case(CASE, id="test-case-0006", base_url="https://automationexercise.com")

    case = CaseFile.from_text(text)

    assert case.id == "test-case-0006"
    assert str(case.base_url) == "https://automationexercise.com/"
    assert case.requirement_ids == ["FR-CNT-01"]
    assert case.test_type == "Functional"
