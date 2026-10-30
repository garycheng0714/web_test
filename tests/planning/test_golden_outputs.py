import difflib
from pathlib import Path

import pytest

from review_helpers import answers_for, make_case, make_design
from web_test.planning.cases_writer import render_document
from web_test.planning.review import JevAnswer, run_review
from web_test.planning.review.report import render_report

GOLDEN = Path(__file__).parent.parent / "fixtures" / "golden"


def _assert_golden(actual: str, name: str) -> None:
    expected = (GOLDEN / name).read_text(encoding="utf-8")
    if actual == expected:
        return
    diff = difflib.unified_diff(
        expected.splitlines(keepends=True),
        actual.splitlines(keepends=True),
        fromfile=f"golden/{name}",
        tofile="actual",
    )
    pytest.fail("output differs from the golden file:\n" + "".join(diff))


def test_review_report_matches_the_golden() -> None:
    record = run_review(
        "# PRD",
        make_design(),
        "artifact",
        system_one=lambda request: answers_for(
            request, ac_2=JevAnswer(0.05), step_3_1_continuity=JevAnswer(0.6)
        ),
    )

    _assert_golden(render_report(record), "review_report_fail.md")


def test_blocked_review_report_matches_the_golden() -> None:
    record = run_review(
        "# PRD",
        make_design(),
        "artifact",
        system_one=lambda request: (_ for _ in ()).throw(RuntimeError("no key")),
    )

    _assert_golden(render_report(record), "review_report_blocked.md")


def test_case_document_matches_the_golden() -> None:
    case = make_case(
        preconditions=["The signup page is open"],
        steps=[
            {"action": "Go", "expected_result": "Page shown"},
            {"action": "a | b", "expected_result": "line\nbreak"},
        ],
        notes="Assumed the form accepts any email.",
    )

    text = render_document(
        [case],
        id="register-login",
        base_url="https://automationexercise.com",
        title="Register Login",
        open_questions=["Does the form accept any email?"],
    )

    _assert_golden(text, "case_document_register_login.md")
