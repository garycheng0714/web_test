from web_test.planning.cases_writer import render_document
from web_test.planning.review.cli import main
from web_test.planning.review.jev import JevAnswer
from web_test.planning.review.local import review_case_file
from web_test.planning.review.verification import VerificationStatus
from web_test.planning.schema import Case


def _case() -> Case:
    return Case.model_validate(
        {
            "requirement_ids": ["FR-1"],
            "module_feature": "Account",
            "test_scenario": "Register",
            "preconditions": ["The signup page is open"],
            "steps": [
                {"action": "Go | home", "expected_result": "Page shown"},
                {"action": "Submit", "expected_result": "Done"},
            ],
            "priority": "High",
            "severity": "Major",
            "test_type": "Functional",
            "notes": "Covers FR-1.",
        }
    )


def _document() -> str:
    return render_document(
        [_case()],
        id="register",
        base_url="https://example.com",
        title="Register",
        open_questions=["What is the password policy?"],
    )


def _files(tmp_path):
    case_path = tmp_path / "case.md"
    prd_path = tmp_path / "prd.md"
    case_path.write_text(_document(), encoding="utf-8")
    prd_path.write_text("# PRD", encoding="utf-8")
    return case_path, prd_path


def test_review_case_file_reviews_the_current_contents(tmp_path):
    case_path, prd_path = _files(tmp_path)

    def system_one(request):
        return {question_id: JevAnswer(0.95) for question_id in request.questions}

    record = review_case_file(case_path, prd_path, system_one=system_one)

    assert record.result.status is VerificationStatus.PASS


def test_review_case_file_sends_an_edited_step_to_jev(tmp_path):
    case_path, prd_path = _files(tmp_path)
    case_path.write_text(
        case_path.read_text(encoding="utf-8").replace("Submit", "Click Submit"),
        encoding="utf-8",
    )
    captured = {}

    def system_one(request):
        captured["request"] = request
        return {question_id: JevAnswer(0.95) for question_id in request.questions}

    review_case_file(case_path, prd_path, system_one=system_one)

    actions = [
        step.action
        for case in captured["request"].subject.cases
        for step in case.steps
    ]
    assert "Click Submit" in actions


def test_cli_reports_a_missing_file(tmp_path, capsys):
    result = main(
        [
            "--case",
            str(tmp_path / "missing-case.md"),
            "--prd",
            str(tmp_path / "missing-prd.md"),
        ]
    )

    assert result == 1
    assert "failed:" in capsys.readouterr().err
