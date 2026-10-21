from web_test.automation.case_file import CaseFile
from web_test.planning.cases_writer import (
    CaseWriter,
    render_case_section,
    render_document,
    title_from_stem,
)
from web_test.planning.schema import Case


def _case(**overrides):
    data = {
        "requirement_ids": ["FR-ACC-01"],
        "module_feature": "Account",
        "test_scenario": "Register",
        "preconditions": ["The signup page is open"],
        "steps": [
            {"action": "Go", "expected_result": "Page shown"},
            {"action": "a | b", "expected_result": "line\nbreak"},
        ],
        "priority": "High",
        "severity": "Critical",
        "test_type": "Functional",
        "notes": "Assumed the form accepts any email.",
        **overrides,
    }
    return Case.model_validate(data)


def test_title_from_stem():
    assert title_from_stem("register-login") == "Register Login"
    assert title_from_stem("contact_us") == "Contact Us"


def test_section_heading_and_metadata_block():
    text = render_case_section(_case(), index=2)

    assert text.startswith("## Case 2: Account: Register\n\n")
    assert "```yaml\nrequirement_ids: [FR-ACC-01]\npriority: High\ntest_type: Functional\n```" in text
    assert "**Severity:** Critical" in text


def test_section_preconditions_block():
    with_preconditions = render_case_section(_case(), index=1)
    without_preconditions = render_case_section(_case(preconditions=[]), index=1)

    assert "### Preconditions\n\n- The signup page is open" in with_preconditions
    assert "### Preconditions" not in without_preconditions


def test_section_steps_table_escapes_cells():
    text = render_case_section(_case(), index=1)

    assert "### Test Steps\n\n| Step | Action | Expected Result |\n| --- | --- | --- |" in text
    assert "| 1 | Go | Page shown |" in text
    assert "| 2 | a \\| b | line break |" in text


def test_section_notes_block():
    with_notes = render_case_section(_case(), index=1)
    without_notes = render_case_section(_case(notes=""), index=1)

    assert "### Notes\n\nAssumed the form accepts any email." in with_notes
    assert "### Notes" not in without_notes


def test_section_blocks_are_separated_by_one_blank_line():
    text = render_case_section(_case(), index=1)

    assert "\n\n\n" not in text
    assert not text.endswith("\n")


def test_render_document_has_front_matter_title_and_case_sections():
    text = render_document(
        [_case(), _case(test_scenario="Login")],
        id="register-login",
        base_url="https://automationexercise.com",
        title="Register Login",
    )

    assert text.startswith(
        "---\nid: register-login\nbase_url: https://automationexercise.com\n---\n\n"
        "# Register Login\n\n## Case 1: Account: Register"
    )
    assert "## Case 2: Account: Login" in text
    assert text.endswith("\n")


def test_render_document_appends_open_questions():
    text = render_document(
        [_case()],
        id="register-login",
        base_url="https://example.com",
        title="Register Login",
        open_questions=["What is the password policy?", "Is the email case-insensitive?"],
    )

    assert "## Open Questions" in text
    assert "- What is the password policy?" in text
    assert text.rstrip().endswith("Is the email case-insensitive?")


def test_render_document_omits_open_questions_when_empty():
    text = render_document(
        [_case()], id="register-login", base_url="https://example.com", title="Register Login"
    )

    assert "## Open Questions" not in text


def test_rendered_front_matter_parses_with_case_file():
    text = render_document(
        [_case()], id="register-login", base_url="https://automationexercise.com", title="Register Login"
    )

    case = CaseFile.from_text(text)

    assert case.id == "register-login"
    assert str(case.base_url) == "https://automationexercise.com/"


def test_case_writer_writes_one_file_and_overwrites(tmp_path):
    writer = CaseWriter(tmp_path, base_url="https://example.com")

    name = writer.write("register-login", [_case(), _case(test_scenario="Login")])

    assert name == "test-case-register-login.md"
    assert [path.name for path in tmp_path.glob("*.md")] == ["test-case-register-login.md"]
    first = (tmp_path / name).read_text(encoding="utf-8")
    assert "# Register Login" in first
    assert "## Case 2: Account: Login" in first

    writer.write("register-login", [_case(test_scenario="Only")])

    second = (tmp_path / name).read_text(encoding="utf-8")
    assert "## Case 2:" not in second
    assert "## Case 1: Account: Only" in second


def test_case_writer_writes_supplied_content_verbatim(tmp_path):
    writer = CaseWriter(tmp_path, base_url="https://example.com")

    name = writer.write("register-login", [_case()], content="# supplied\n")

    assert (tmp_path / name).read_text(encoding="utf-8") == "# supplied\n"
