import re

from web_test.planning.cases_writer import render_document
from web_test.planning.review.parser import parse_test_case
from web_test.planning.review.structure import CHECK_SET_VERSION, structure_checks
from web_test.planning.review.verification import VerificationStatus
from web_test.planning.schema import Case
from review_helpers import make_case


def _document(cases: list[Case] | None = None) -> str:
    return render_document(
        cases or [make_case()],
        id="demo",
        base_url="https://example.com",
        title="Demo",
    )


def _by_id(text: str):
    subject = parse_test_case(text, "# PRD")
    return {outcome.check_id: outcome for outcome in structure_checks(subject, text)}


def test_structure_checks_pass_a_clean_document() -> None:
    outcomes = _by_id(_document())

    assert CHECK_SET_VERSION
    assert outcomes["front_matter_id"].status is VerificationStatus.PASS
    assert outcomes["front_matter_base_url"].status is VerificationStatus.PASS
    assert outcomes["case_numbers"].status is VerificationStatus.PASS
    assert outcomes["step_1_1_action"].status is VerificationStatus.PASS
    assert outcomes["step_1_1_expected"].status is VerificationStatus.PASS


def test_front_matter_is_required() -> None:
    text = re.sub(r"\A---\n.*?\n---\n", "", _document(), count=1, flags=re.S)

    outcomes = _by_id(text)

    assert outcomes["front_matter"].status is VerificationStatus.FAIL
    assert "missing or invalid" in outcomes["front_matter"].detail


def test_base_url_is_required() -> None:
    text = _document().replace("base_url: https://example.com\n", "")

    outcomes = _by_id(text)

    assert outcomes["front_matter_id"].status is VerificationStatus.PASS
    assert outcomes["front_matter_base_url"].status is VerificationStatus.FAIL
    assert "base_url" in outcomes["front_matter_base_url"].detail


def test_case_numbers_are_unique() -> None:
    text = _document([make_case(), make_case()]).replace("## Case 2:", "## Case 1:")

    outcomes = _by_id(text)

    assert outcomes["case_numbers"].status is VerificationStatus.FAIL
    assert "duplicate case numbers: 1" in outcomes["case_numbers"].detail


def test_step_action_and_expected_result_are_required() -> None:
    outcomes = _by_id(_document([make_case(steps=[{"action": "", "expected_result": ""}])]))

    assert outcomes["step_1_1_action"].status is VerificationStatus.FAIL
    assert outcomes["step_1_1_expected"].status is VerificationStatus.FAIL
    assert outcomes["step_1_1_action"].detail == "action is empty"
    assert outcomes["step_1_1_expected"].detail == "expected result is empty"


def test_text_without_case_sections_has_no_structure_checks() -> None:
    subject = parse_test_case(_document(), "# PRD")

    assert structure_checks(subject, "artifact") == ()


def test_a_case_needs_at_least_one_step() -> None:
    empty_case = make_case(steps=[])
    outcomes = _by_id(_document([empty_case]))

    assert outcomes["case_1_steps"].status is VerificationStatus.FAIL
    assert outcomes["case_1_steps"].detail == "case has no steps"
