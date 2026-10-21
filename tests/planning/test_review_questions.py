from web_test.planning.review import JevAnswer, run_review
from web_test.planning.review_questions import STEP_QUALITY_DIMENSIONS, expected_checks, questions_for_subject
from web_test.planning.schema import Case, DesignOutput
from web_test.planning.verification import CheckDimension


def _case(**overrides):
    data = {
        "requirement_ids": ["FR-ACC-01"],
        "module_feature": "Account",
        "test_scenario": "Register",
        "steps": [
            {"action": "Go", "expected_result": "Page shown"},
            {"action": "Submit", "expected_result": "Done"},
        ],
        "priority": "High",
        "severity": "Critical",
        "test_type": "Functional",
        **overrides,
    }
    return Case.model_validate(data)


def _subject():
    captured = {}

    def system_one(request):
        captured["request"] = request
        return {question_id: JevAnswer(0.95) for question_id in request.questions}

    design = DesignOutput(cases=[_case(), _case(test_scenario="Login")])
    run_review("# PRD", design, "artifact", system_one=system_one)
    return captured["request"].subject


def test_questions_for_subject_matches_expected_checks():
    subject = _subject()

    assert set(questions_for_subject(subject)) == {
        spec.question_id for spec in expected_checks(subject)
    }


def test_every_step_has_every_check():
    subject = _subject()
    specs = expected_checks(subject)

    step_specs = [
        spec for spec in specs if spec.dimension is not CheckDimension.AC_ALIGNMENT
    ]
    assert [spec.dimension for spec in step_specs].count(
        CheckDimension.STEP_REASONABLE
    ) == 4
    assert {spec.dimension for spec in step_specs} == set(STEP_QUALITY_DIMENSIONS)
