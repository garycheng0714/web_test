from web_test.automation.case_file import CaseFile
from web_test.planning.cases_writer import CaseWriter, assign_ids, render_case
from web_test.planning.schema import Case


def _case(**overrides):
    data = {
        "requirement_ids": ["FR-ACC-01"],
        "module_feature": "Account",
        "test_scenario": "Register",
        "steps": [{"action": "Go", "expected_result": "Page shown"}],
        "priority": "High",
        "severity": "Critical",
        "test_type": "Functional",
        "notes": "Assumed the form accepts any email.",
        **overrides,
    }
    return Case.model_validate(data)


def test_render_case_matches_the_reference_format():
    text = render_case(_case(), id="test-case-0004", base_url="https://automationexercise.com")

    assert text.startswith(
        "---\n"
        "id: test-case-0004\n"
        "base_url: https://automationexercise.com\n"
        "requirement_ids: [FR-ACC-01]\n"
        "priority: High\n"
        "test_type: Functional\n"
        "---\n"
    )
    assert "# Account: Register" in text
    assert "**Severity:** Critical" in text
    assert "| Step | Action | Expected Result |" in text
    assert "| 1 | Go | Page shown |" in text
    assert "## Notes" in text
    assert "Assumed the form accepts any email." in text


def test_render_case_omits_empty_sections_and_escapes_pipes():
    case = _case(
        preconditions=[],
        notes="",
        steps=[{"action": "a | b", "expected_result": "line\nbreak"}],
    )

    text = render_case(case, id="test-case-0005", base_url="https://example.com")

    assert "## Preconditions" not in text
    assert "## Notes" not in text
    assert "| 1 | a \\| b | line break |" in text


def test_rendered_front_matter_parses_with_case_file():
    text = render_case(_case(), id="test-case-0006", base_url="https://automationexercise.com")

    case = CaseFile.from_text(text)

    assert case.id == "test-case-0006"
    assert str(case.base_url) == "https://automationexercise.com/"
    assert case.requirement_ids == ["FR-ACC-01"]
    assert case.test_type == "Functional"


def test_assign_ids_starts_after_the_highest_existing():
    assert assign_ids(["test-case-0002.md", "test-case-0007.md", "readme.md"], 2) == [
        "test-case-0008",
        "test-case-0009",
    ]


def test_assign_ids_starts_at_one_when_empty():
    assert assign_ids([], 1) == ["test-case-0001"]


def test_case_writer_writes_sequential_files(tmp_path):
    names = CaseWriter(tmp_path, base_url="https://example.com").write(
        [_case(), _case(test_scenario="Login")]
    )

    assert names == ["test-case-0001.md", "test-case-0002.md"]
    first = CaseFile.from_text((tmp_path / names[0]).read_text(encoding="utf-8"))
    assert first.id == "test-case-0001"
    assert str(first.base_url) == "https://example.com/"
    assert "# Account: Login" in (tmp_path / names[1]).read_text(encoding="utf-8")


def test_case_writer_continues_after_existing(tmp_path):
    (tmp_path / "test-case-0003.md").write_text("x", encoding="utf-8")

    names = CaseWriter(tmp_path, base_url="https://example.com").write([_case()])

    assert names == ["test-case-0004.md"]
